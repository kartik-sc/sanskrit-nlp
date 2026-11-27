
import argparse
import json
import hashlib
from pathlib import Path
from collections import Counter

from datasets import load_dataset
from huggingface_hub import HfApi


# --------------------------------------------------
# 1. Command-line arguments
# --------------------------------------------------

parser = argparse.ArgumentParser(
    description="Acquire Sanskrit corpus from AI4Bharat Sangraha"
)

parser.add_argument("--target-tokens", type=int, default=100_000)
parser.add_argument("--name", default="pilot")
parser.add_argument("--seed", type=int, default=42)
parser.add_argument("--shuffle", action="store_true")
parser.add_argument("--buffer-size", type=int, default=10_000)
parser.add_argument("--revision", type=str, default=None)

args = parser.parse_args()

if args.target_tokens <= 0:
    parser.error("--target-tokens must be positive")

if args.buffer_size <= 0:
    parser.error("--buffer-size must be positive")

if not args.name or Path(args.name).name != args.name:
    parser.error("--name must be a valid file name")


# --------------------------------------------------
# 2. Output directories
# --------------------------------------------------

raw_dir = Path("data/raw")
interim_dir = Path("data/interim")
metrics_dir = Path("results/metrics")

for directory in [raw_dir, interim_dir, metrics_dir]:
    directory.mkdir(parents=True, exist_ok=True)

raw_path = raw_dir / f"{args.name}.jsonl"
text_path = interim_dir / f"{args.name}.txt"
stats_path = metrics_dir / f"{args.name}_acquisition.json"


# --------------------------------------------------
# 3. Prevent accidental overwrites
# --------------------------------------------------

for path in [raw_path, text_path, stats_path]:
    if path.exists():
        raise FileExistsError(
            f"Refusing to overwrite existing file: {path}"
        )


# --------------------------------------------------
# 4. Resolve and pin dataset revision
# --------------------------------------------------

dataset_id = "ai4bharat/sangraha"

revision = HfApi().dataset_info(
    dataset_id,
    revision=args.revision,
).sha

source = (
    f"hf://datasets/{dataset_id}@{revision}/"
    "verified/san/*.parquet"
)

print(f"Dataset: {dataset_id}")
print(f"Revision: {revision}")
print(f"Target tokens: {args.target_tokens:,}")
print(f"Sampling: {'buffered shuffle' if args.shuffle else 'sequential'}")
print(f"Corpus name: {args.name}")


# --------------------------------------------------
# 5. Load streaming dataset
# --------------------------------------------------

dataset = load_dataset(
    "parquet",
    data_files={"train": source},
    split="train",
    streaming=True,
)

if args.shuffle:
    dataset = dataset.shuffle(
        seed=args.seed,
        buffer_size=args.buffer_size,
    )

    print(f"Random seed: {args.seed}")
    print(f"Shuffle buffer: {args.buffer_size:,}")

print("\nStarting corpus acquisition...", flush=True)


# --------------------------------------------------
# 6. Initialize acquisition statistics
# --------------------------------------------------

total_tokens = 0
total_documents = 0
total_characters = 0

source_types = Counter()
source_tokens = Counter()


# --------------------------------------------------
# 7. Acquire corpus
# --------------------------------------------------

with (
    raw_path.open("w", encoding="utf-8", newline="\n") as raw_file,
    text_path.open("w", encoding="utf-8", newline="\n") as text_file,
):
    for row in dataset:
        text = row["text"]

        if not text or not text.strip():
            continue

        tokens = len(text.split())
        source_type = row.get("type") or "unknown"

        # Preserve original record and metadata
        raw_file.write(
            json.dumps(row, ensure_ascii=False) + "\n"
        )

        # Normalize line endings only; no linguistic cleaning
        plain_text = text.replace("\r\n", "\n").replace("\r", "\n")
        text_file.write(plain_text + "\n\n")

        total_tokens += tokens
        total_documents += 1
        total_characters += len(text)

        source_types[source_type] += 1
        source_tokens[source_type] += tokens

        if total_documents % 100 == 0:
            progress = total_tokens / args.target_tokens * 100

            print(
                f"Documents: {total_documents:,} | "
                f"Tokens: {total_tokens:,} | "
                f"Progress: {progress:.2f}%",
                flush=True,
            )

        if total_tokens >= args.target_tokens:
            break


# --------------------------------------------------
# 8. Generate SHA-256 checksums
# --------------------------------------------------

def sha256(path):
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024), b""
        ):
            digest.update(chunk)

    return digest.hexdigest()


# --------------------------------------------------
# 9. Save acquisition metadata
# --------------------------------------------------

stats = {
    "dataset": dataset_id,
    "subset": "verified/san",
    "revision": revision,
    "source": source,
    "sampling": (
        "buffered_shuffle" if args.shuffle
        else "sequential"
    ),
    "seed": args.seed if args.shuffle else None,
    "buffer_size": args.buffer_size if args.shuffle else None,
    "target_tokens": args.target_tokens,
    "documents": total_documents,
    "whitespace_tokens": total_tokens,
    "code_points": total_characters,
    "source_types": dict(source_types),
    "source_tokens": dict(source_tokens),
    "raw_file": str(raw_path),
    "raw_bytes": raw_path.stat().st_size,
    "raw_sha256": sha256(raw_path),
    "text_file": str(text_path),
    "text_bytes": text_path.stat().st_size,
    "text_sha256": sha256(text_path),
    "encoding": "UTF-8",
    "line_endings": "LF",
    "target_reached": total_tokens >= args.target_tokens,
}

stats_path.write_text(
    json.dumps(stats, indent=2, ensure_ascii=False),
    encoding="utf-8",
)


# --------------------------------------------------
# 10. Final acquisition summary
# --------------------------------------------------

if total_tokens < args.target_tokens:
    raise RuntimeError(
        "Dataset exhausted before reaching target"
    )

print("\nAcquisition complete.")
print(json.dumps(stats, indent=2, ensure_ascii=False))
