
import argparse
import json
import hashlib
import unicodedata
from pathlib import Path
from collections import Counter

import regex


parser = argparse.ArgumentParser(
    description="Refined Sanskrit lexical cleaning"
)

parser.add_argument(
    "--input",
    default="data/processed/normalized_corpus.jsonl",
)

parser.add_argument(
    "--output",
    default="data/processed/clean_corpus_v2.txt",
)

parser.add_argument(
    "--metrics",
    default="results/metrics/working_1m_cleaning_v2.json",
)

args = parser.parse_args()

input_path = Path(args.input)
output_path = Path(args.output)
metrics_path = Path(args.metrics)

for path in [output_path, metrics_path]:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite: {path}")

    path.parent.mkdir(parents=True, exist_ok=True)


# Devanagari letters
devanagari_letter = regex.compile(
    r"[\p{Script=Devanagari}&&\p{L}]",
    flags=regex.V1,
)

# Devanagari letters and marks
devanagari_character = regex.compile(
    r"[\p{Script=Devanagari}&&[\p{L}\p{M}]]",
    flags=regex.V1,
)

latin = regex.compile(r"\p{Script=Latin}")
number = regex.compile(r"\p{N}")

punctuation_only = regex.compile(r"^\p{P}+$")
punctuation_edges = regex.compile(r"^\p{P}+|\p{P}+$")

# Selected internal punctuation separators
internal_separator = regex.compile(
    r'[-‐‑‒–—।॥,;:!?."“”]+'
)

# Additional Vedic accent marks
vedic_marks = {"\u0951", "\u0952"}

join_controls = {"\u200c", "\u200d"}

stats = Counter()

normalized_counts = Counter()
cleaned_counts = Counter()

examples = {}


def record(category, example):
    stats[category] += 1

    items = examples.setdefault(category, [])

    if len(items) < 20 and example not in items:
        items.append(example)


def valid_word(word):
    if not devanagari_letter.search(word):
        return False

    for char in word:
        if devanagari_character.fullmatch(char):
            continue

        if char in vedic_marks:
            continue

        if char in join_controls:
            continue

        # Combining marks in Vedic Extensions
        if (
            "\u1cd0" <= char <= "\u1cff"
            and unicodedata.category(char).startswith("M")
        ):
            continue

        return False

    return True


def clean_token(token):
    if punctuation_only.fullmatch(token):
        record("removed_punctuation_only", token)
        return []

    candidate = punctuation_edges.sub("", token)

    if not candidate:
        record("removed_empty", token)
        return []

    # Avoid speculative OCR correction.
    if latin.search(candidate):
        record("removed_latin_tokens", token)
        return []

    if number.search(candidate):
        record("removed_numeric_tokens", token)
        return []

    # Preserve already valid word forms.
    if valid_word(candidate):
        if candidate != token:
            stats["stripped_edge_punctuation"] += 1

        if any(
            char in vedic_marks
            or "\u1cd0" <= char <= "\u1cff"
            for char in candidate
        ):
            record("retained_vedic_tokens", candidate)

        return [candidate]

    # Recover words separated by punctuation.
    parts = [
        part
        for part in internal_separator.split(candidate)
        if part
    ]

    if len(parts) > 1 and all(
        valid_word(part) for part in parts
    ):
        record("recovered_split_tokens", token)
        stats["words_from_split_tokens"] += len(parts)
        return parts

    record("removed_invalid_tokens", token)
    return []


with (
    input_path.open("r", encoding="utf-8") as source,
    output_path.open(
        "w", encoding="utf-8", newline="\n"
    ) as output,
):
    for line in source:
        row = json.loads(line)

        stats["documents"] += 1

        tokens = row["text"].split()
        normalized_counts.update(tokens)

        cleaned = []

        for token in tokens:
            cleaned.extend(clean_token(token))

        cleaned_counts.update(cleaned)

        if cleaned:
            output.write(" ".join(cleaned) + "\n\n")
        else:
            stats["empty_documents"] += 1

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
    "output": str(output_path),
    "version": "v2",
    "transformations": dict(stats),
    "normalized": summarize(normalized_counts),
    "lexical_cleaned": summarize(cleaned_counts),
    "examples": examples,
    "output_bytes": output_path.stat().st_size,
    "sha256": hashlib.file_digest(
        output_path.open("rb"), "sha256"
    ).hexdigest(),
    "encoding": "UTF-8",
    "line_endings": "LF",
}

metrics_path.write_text(
    json.dumps(results, indent=2, ensure_ascii=False),
    encoding="utf-8",
)

print("\nV2 cleaning complete.")
print(json.dumps(results["lexical_cleaned"], ensure_ascii=False))
print(f"Metrics: {metrics_path}")
