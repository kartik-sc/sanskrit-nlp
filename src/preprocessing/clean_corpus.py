
import argparse
import json
import unicodedata
from collections import Counter
from pathlib import Path

import regex


parser = argparse.ArgumentParser(
    description="Conservative Sanskrit corpus cleaning"
)

parser.add_argument(
    "--input",
    default="data/raw/working_1m.jsonl",
)

parser.add_argument(
    "--output-dir",
    default="data/processed",
)

parser.add_argument(
    "--metrics",
    default="results/metrics/working_1m_cleaning.json",
)

args = parser.parse_args()

input_path = Path(args.input)
output_dir = Path(args.output_dir)
metrics_path = Path(args.metrics)

output_dir.mkdir(parents=True, exist_ok=True)
metrics_path.parent.mkdir(parents=True, exist_ok=True)

normalized_path = output_dir / "normalized_corpus.jsonl"
sentence_path = output_dir / "sentence_ready.txt"
lexical_path = output_dir / "clean_corpus.txt"

for path in [
    normalized_path,
    sentence_path,
    lexical_path,
    metrics_path,
]:
    if path.exists():
        raise FileExistsError(
            f"Refusing to overwrite: {path}"
        )

# Sanskrit lexical candidates:
# Devanagari letters and combining marks.
devanagari_word = regex.compile(
    r"[\p{Script=Devanagari}&&[\p{L}\p{M}]]+",
    flags=regex.V1,
)

devanagari_letter = regex.compile(
    r"[\p{Script=Devanagari}&&\p{L}]",
    flags=regex.V1,
)

number = regex.compile(r"\p{N}")
latin = regex.compile(r"\p{Script=Latin}")
punctuation_only = regex.compile(r"^\p{P}+$")

# Preserve internal avagraha and join controls.
punctuation_edges = regex.compile(
    r"^\p{P}+|\p{P}+$"
)

stats = Counter()
stage_counts = {
    "raw": Counter(),
    "normalized": Counter(),
    "punctuation_removed": Counter(),
    "lexical_cleaned": Counter(),
}

removed_examples = {}


def record_removal(reason, token):
    stats[reason] += 1

    examples = removed_examples.setdefault(reason, [])

    if token not in examples and len(examples) < 20:
        examples.append(token)


def normalize_text(text):
    text = unicodedata.normalize("NFC", text)

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Replace unwanted control characters with spaces.
    # Preserve newlines, tabs and Sanskrit join controls.
    text = "".join(
        " "
        if unicodedata.category(char).startswith("C")
        and char not in "\n\t\u200c\u200d"
        else char
        for char in text
    )

    # Normalize horizontal whitespace.
    text = regex.sub(r"[^\S\n]+", " ", text)

    return text.strip()


def lexical_clean(tokens):
    cleaned = []

    for token in tokens:
        if punctuation_only.fullmatch(token):
            record_removal("removed_punctuation_only", token)
            continue

        # Strip surrounding punctuation, not internal
        # punctuation or characters.
        candidate = punctuation_edges.sub("", token)

        if not candidate:
            record_removal("removed_empty", token)
            continue

        stage_counts["punctuation_removed"][candidate] += 1

        if latin.search(candidate):
            record_removal("removed_latin_tokens", token)
            continue

        if number.search(candidate):
            record_removal("removed_numeric_tokens", token)
            continue

        # Ignore join controls when validating script.
        validation = candidate.replace("\u200c", "")
        validation = validation.replace("\u200d", "")

        if not devanagari_word.fullmatch(validation):
            record_removal("removed_non_devanagari", token)
            continue

        if not devanagari_letter.search(validation):
            record_removal("removed_mark_only", token)
            continue

        if candidate != token:
            stats["tokens_with_stripped_punctuation"] += 1

        cleaned.append(candidate)

    return cleaned


with (
    input_path.open("r", encoding="utf-8") as source,
    normalized_path.open(
        "w", encoding="utf-8", newline="\n"
    ) as normalized_file,
    sentence_path.open(
        "w", encoding="utf-8", newline="\n"
    ) as sentence_file,
    lexical_path.open(
        "w", encoding="utf-8", newline="\n"
    ) as lexical_file,
):
    for line in source:
        row = json.loads(line)
        original = row["text"]

        stats["documents"] += 1

        raw_tokens = original.split()
        stage_counts["raw"].update(raw_tokens)

        normalized = normalize_text(original)
        normalized_tokens = normalized.split()

        stage_counts["normalized"].update(
            normalized_tokens
        )

        if original != normalized:
            stats["normalized_documents"] += 1

        # Preserve metadata and record boundaries.
        normalized_row = dict(row)
        normalized_row["text"] = normalized

        normalized_file.write(
            json.dumps(
                normalized_row,
                ensure_ascii=False,
            ) + "\n"
        )

        # Preserve sentence-boundary punctuation.
        sentence_file.write(normalized + "\n\n")

        cleaned_tokens = lexical_clean(normalized_tokens)

        stage_counts["lexical_cleaned"].update(
            cleaned_tokens
        )

        if cleaned_tokens:
            lexical_file.write(
                " ".join(cleaned_tokens) + "\n\n"
            )
        else:
            stats["empty_lexical_documents"] += 1

        if stats["documents"] % 200 == 0:
            print(
                f"Processed {stats['documents']:,} records",
                flush=True,
            )


def summarize(counter):
    tokens = sum(counter.values())
    types = len(counter)

    return {
        "tokens": tokens,
        "types": types,
        "type_token_ratio": types / tokens if tokens else 0,
        "top_20": counter.most_common(20),
    }


results = {
    "input": str(input_path),
    "transformations": dict(stats),
    "stages": {
        name: summarize(counter)
        for name, counter in stage_counts.items()
    },
    "removed_examples": removed_examples,
    "outputs": {
        "normalized_jsonl": str(normalized_path),
        "sentence_ready": str(sentence_path),
        "lexical_corpus": str(lexical_path),
    },
}

metrics_path.write_text(
    json.dumps(
        results,
        indent=2,
        ensure_ascii=False,
    ),
    encoding="utf-8",
)

print("\nCleaning complete.")

for name, stage in results["stages"].items():
    print(
        f"{name}: "
        f"{stage['tokens']:,} tokens | "
        f"{stage['types']:,} types | "
        f"TTR={stage['type_token_ratio']:.4f}"
    )

print(f"\nMetrics saved to: {metrics_path}")
