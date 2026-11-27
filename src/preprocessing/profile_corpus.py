
import argparse
import json
import unicodedata
from pathlib import Path
from collections import Counter

import regex


parser = argparse.ArgumentParser(
    description="Profile Sanskrit corpus quality"
)

parser.add_argument(
    "--input",
    default="data/raw/working_1m.jsonl"
)

parser.add_argument(
    "--output",
    default="results/metrics/working_1m_profile.json"
)

args = parser.parse_args()

input_path = Path(args.input)
output_path = Path(args.output)

output_path.parent.mkdir(parents=True, exist_ok=True)


# Unicode patterns
devanagari = regex.compile(r"\p{Script=Devanagari}")
latin = regex.compile(r"\p{Script=Latin}")
number = regex.compile(r"\p{N}")
punctuation = regex.compile(r"^\p{P}+$")
numeric_token = regex.compile(r"^\p{N}+$")


# Statistics
documents = 0
total_tokens = 0

token_counts = Counter()
character_counts = Counter()
noise_counts = Counter()
punctuation_counts = Counter()

source_stats = {}

seen_texts = set()
seen_ids = set()

duplicate_texts = 0
duplicate_ids = 0

examples = {}


def record_noise(category, token):
    noise_counts[category] += 1

    if category not in examples:
        examples[category] = []

    if (
        len(examples[category]) < 20
        and token not in examples[category]
    ):
        examples[category].append(token)


with input_path.open("r", encoding="utf-8") as file:

    for line in file:
        row = json.loads(line)

        text = row["text"]
        doc_id = row["doc_id"]
        source = row.get("type") or "unknown"

        documents += 1

        if doc_id in seen_ids:
            duplicate_ids += 1

        seen_ids.add(doc_id)

        if text in seen_texts:
            duplicate_texts += 1

        seen_texts.add(text)

        tokens = text.split()
        total_tokens += len(tokens)

        if source not in source_stats:
            source_stats[source] = Counter()

        source_stats[source]["documents"] += 1
        source_stats[source]["tokens"] += len(tokens)

        token_counts.update(tokens)

        # Character-level profiling
        for char in text:

            if char.isspace():
                category = "whitespace"

            elif number.fullmatch(char):
                category = "numeric"

            elif devanagari.fullmatch(char):
                category = "devanagari"

            elif latin.fullmatch(char):
                category = "latin"

            elif unicodedata.category(char).startswith("P"):
                category = "punctuation"

            elif unicodedata.category(char).startswith("C"):
                category = "control_or_format"

            else:
                category = "other"

            character_counts[category] += 1

            if unicodedata.category(char).startswith("P"):
                punctuation_counts[char] += 1

        # Token-level profiling
        for token in tokens:

            has_dev = bool(devanagari.search(token))
            has_latin = bool(latin.search(token))

            if numeric_token.fullmatch(token):
                record_noise("numeric_only", token)

            if punctuation.fullmatch(token):
                record_noise("punctuation_only", token)

            if has_latin:
                record_noise("contains_latin", token)
                source_stats[source]["latin_tokens"] += 1

            if has_dev and has_latin:
                record_noise("mixed_devanagari_latin", token)

            if not has_dev:
                record_noise("no_devanagari", token)

            if number.search(token):
                record_noise("contains_number", token)


total_characters = sum(character_counts.values())

results = {
    "input": str(input_path),
    "documents": documents,
    "total_tokens": total_tokens,
    "unique_types": len(token_counts),

    "type_token_ratio": (
        len(token_counts) / total_tokens
        if total_tokens else 0
    ),

    "duplicate_document_ids": duplicate_ids,
    "duplicate_text_records": duplicate_texts,

    "total_code_points": total_characters,

    "character_distribution": {
        key: {
            "count": value,
            "percentage": round(
                value / total_characters * 100, 4
            ) if total_characters else 0
        }
        for key, value in character_counts.items()
    },

    "noise_categories": {
        key: {
            "count": value,
            "percentage": round(
                value / total_tokens * 100, 4
            ) if total_tokens else 0
        }
        for key, value in noise_counts.items()
    },

    "punctuation_frequencies": dict(
        punctuation_counts.most_common(30)
    ),

    "source_statistics": {
        key: dict(value)
        for key, value in source_stats.items()
    },

    "most_frequent_tokens": token_counts.most_common(30),

    "noise_examples": examples,
}


output_path.write_text(
    json.dumps(
        results,
        indent=2,
        ensure_ascii=False
    ),
    encoding="utf-8"
)

print("Corpus profiling complete.")
print(f"Documents: {documents:,}")
print(f"Tokens: {total_tokens:,}")
print(f"Unique types: {len(token_counts):,}")
print(f"TTR: {results['type_token_ratio']:.4f}")
print(f"Duplicate IDs: {duplicate_ids:,}")
print(f"Duplicate texts: {duplicate_texts:,}")
print(f"Results saved to: {output_path}")
