
import argparse
import json
import hashlib
from pathlib import Path
from collections import Counter

from datasets import load_dataset


parser = argparse.ArgumentParser()
parser.add_argument("--target-tokens", type=int, default=100_000)
parser.add_argument("--name", default="pilot")
args = parser.parse_args()

raw_dir = Path("data/raw")
interim_dir = Path("data/interim")
metrics_dir = Path("results/metrics")

for directory in [raw_dir, interim_dir, metrics_dir]:
    directory.mkdir(parents=True, exist_ok=True)

raw_path = raw_dir / f"{args.name}.jsonl"
text_path = interim_dir / f"{args.name}.txt"
stats_path = metrics_dir / f"{args.name}_acquisition.json"

source = (
    "hf://datasets/ai4bharat/sangraha/"
    "verified/san/*.parquet"
)

dataset = load_dataset(
    "parquet",
    data_files={"train": source},
    split="train",
    streaming=True,
)

total_tokens = 0
total_documents = 0
total_characters = 0
source_types = Counter()

with (
    raw_path.open("w", encoding="utf-8", newline="\n") as raw_file,
    text_path.open("w", encoding="utf-8", newline="\n") as text_file,
):
    for row in dataset:
        text = row["text"]

        if not text or not text.strip():
            continue

        tokens = len(text.split())

        raw_file.write(
            json.dumps(row, ensure_ascii=False) + "\n"
        )

        text_file.write(text + "\n\n")

        total_tokens += tokens
        total_documents += 1
        total_characters += len(text)
        source_types[row.get("type") or "unknown"] += 1

        if total_documents % 100 == 0:
            print(
                f"Documents: {total_documents:,} | "
                f"Tokens: {total_tokens:,}",
                flush=True,
            )

        if total_tokens >= args.target_tokens:
            break


def sha256(path):
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


stats = {
    "dataset": "ai4bharat/sangraha",
    "subset": "verified/san",
    "source": source,
    "sampling": "sequential",
    "target_tokens": args.target_tokens,
    "documents": total_documents,
    "whitespace_tokens": total_tokens,
    "code_points": total_characters,
    "source_types": dict(source_types),
    "raw_file": str(raw_path),
    "raw_bytes": raw_path.stat().st_size,
    "raw_sha256": sha256(raw_path),
    "text_file": str(text_path),
    "text_bytes": text_path.stat().st_size,
    "text_sha256": sha256(text_path),
    "encoding": "UTF-8",
}

stats_path.write_text(
    json.dumps(stats, indent=2),
    encoding="utf-8",
)

print("\nAcquisition complete.")
print(json.dumps(stats, indent=2))

if total_tokens < args.target_tokens:
    raise RuntimeError("Dataset exhausted before reaching target")