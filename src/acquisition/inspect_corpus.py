
import sys
from itertools import islice
from datasets import load_dataset

sys.stdout.reconfigure(encoding="utf-8")

dataset = load_dataset(
    "parquet",
    data_files={
        "train": (
            "hf://datasets/ai4bharat/sangraha/"
            "verified/san/*.parquet"
        )
    },
    split="train",
    streaming=True,
)

print("Dataset features:")
print(dataset.features)

for i, row in enumerate(islice(dataset, 5), start=1):
    text = row["text"]

    print("\n" + "=" * 60)
    print(f"Document: {i}")
    print(f"Available fields: {list(row.keys())}")

    for key, value in row.items():
        if key != "text":
            print(f"{key}: {value}")

    print(f"Code points: {len(text):,}")
    print(f"Whitespace tokens: {len(text.split()):,}")

    print("\nText preview:")
    print(text[:1500])