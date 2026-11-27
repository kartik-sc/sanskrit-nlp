# Project Context — Sanskrit NLP Experiential Learning

## 1. Objective

We are a team of three engineering students working on a two-phase NLP experiential learning project.

Our selected language is Sanskrit, primarily in Devanagari script. We aim to build a research-oriented, reproducible NLP pipeline without unnecessary engineering complexity.

## 2. Phase 1 Requirements

1. Collect a large text corpus.
2. Convert it to UTF-8 plain text with Unix line endings.
3. Perform type-token analysis.
4. Calculate word frequencies and sort in decreasing order.
5. Calculate vocabulary coverage at 10%, 25%, 50%, 75%, 90%, 95% and 99%.
6. Make scientific observations and draw meaningful inferences.
7. Identify corpus noise, clean the corpus and repeat the analyses.
8. Segment paragraphs into sentences, with one sentence per line.
9. Perform word length and sentence length analysis and generate graphs.
10. Prepare a detailed scientific report.

Phase 2 will involve word embeddings, language models, neural networks and named entity recognition.

## 3. Technical Stack

- Python
- Git and GitHub
- DVC for dataset versioning
- DagsHub for shared dataset storage
- Hugging Face Datasets and PyArrow
- regex, NumPy, Pandas, Matplotlib
- Jupyter and pytest
- Windows and WSL/Linux development environments

MLflow and TensorBoard are deferred until needed. Avoid unnecessary frameworks, infrastructure and dependencies.

GitHub: [https://github.com/kartik-sc/sanskrit-nlp](https://github.com/kartik-sc/sanskrit-nlp)

## 4. Dataset

Primary source: AI4Bharat Sangraha

Dataset: [https://huggingface.co/datasets/ai4bharat/sangraha](https://huggingface.co/datasets/ai4bharat/sangraha)

Subset: verified/san

Source files:
hf://datasets/ai4bharat/sangraha/verified/san/\*.parquet

The dataset is accessed through streaming Parquet records with the following schema:

- doc_id: unique record identifier
- text: Sanskrit text
- type: source format (e.g. pdf or web)

A 100K-token pilot corpus has been successfully acquired using sequential streaming.

## 5. Completed Work

- GitHub repository initialized.
- Python environment and dependencies configured.
- DVC and DagsHub configured.
- Dataset accessibility and schema verified.
- Five initial records manually inspected.
- Pilot corpus acquisition script implemented.
- Pilot corpus successfully downloaded.
- UTF-8 encoding validated using iconv.
- Plain-text format verified using file.
- Unix LF line endings verified.
- Python token count independently verified using wc.
- SHA-256 checksums generated.

Pilot corpus publication through DVC is pending confirmation.

## 6. Actual Pilot Corpus Statistics

| Metric              |     Value |
| ------------------- | --------: |
| Records             |       198 |
| Whitespace tokens   |   100,424 |
| Unicode code points |   840,721 |
| PDF records         |       184 |
| Web records         |        14 |
| Plain-text lines    |     3,327 |
| Raw JSONL bytes     | 2,314,678 |
| Plain-text bytes    | 2,290,396 |
| CRLF line endings   |         0 |
| CR characters       |         0 |

The current pilot uses sequential sampling and is intended for development, not as a statistically representative sample of Sanskrit literature.

## 7. Repository Structure

```text
sanskrit-nlp/
├── data/
│   ├── raw/
│   │   └── pilot.jsonl
│   ├── interim/
│   │   └── pilot.txt
│   └── processed/
├── src/
│   ├── acquisition/
│   │   ├── inspect_corpus.py
│   │   └── download_corpus.py
│   ├── preprocessing/
│   ├── analysis/
│   └── segmentation/
├── results/
│   ├── metrics/
│   │   └── pilot_acquisition.json
│   ├── tables/
│   └── plots/
├── notebooks/
├── tests/
├── docs/
├── .dvc/
├── requirements.txt
└── README.md
```

## 8. Observed Data-Quality Issues

Actual inspection revealed:

- OCR errors.
- Incorrectly split words.
- Editorial footnotes and references.
- Arabic and Devanagari numerals.
- Latin characters.
- Inconsistent punctuation.
- Possible Prakrit quotations embedded in Sanskrit commentary.
- Classical prose and verse.
- Very long lines that cannot be treated as individual sentences.
- Complex Sanskrit compounds and sandhi.

Devanagari is a script, not a language. Script-based filtering alone cannot ensure Sanskrit language purity.

## 9. Shared Data Contract

- Pilot input: data/interim/pilot.txt
- Original records: data/raw/pilot.jsonl
- Encoding: UTF-8
- Line endings: LF
- Baseline tokenization: Python str.split()
- Expected baseline token count: 100,424
- Proposed cleaned corpus: data/processed/clean_corpus.txt
- Proposed sentence corpus: data/processed/sentences.txt
- Metrics: JSON
- Frequency tables: CSV
- Graphs: PNG

All scripts must accept configurable input/output paths to support both pilot and full-size corpora.

Preserve original data and document boundaries. Do not overwrite raw files.

## 10. Team Responsibilities

**Member 1 — Data Engineering**

- Corpus acquisition and scaling.
- Data-quality profiling.
- Cleaning and Unicode normalization.
- Dataset versioning and reproducibility.
- Integration.

**Member 2 — Lexical Analysis**

- Type-token analysis and TTR.
- Frequency distributions.
- Vocabulary coverage analysis.
- Zipf's law and coverage graphs.
- Comparison before and after cleaning.

**Member 3 — Linguistic Processing**

- Sentence segmentation.
- Sanskrit punctuation handling.
- Word and sentence length analysis.
- Distribution graphs.
- Segmentation validation and error analysis.

Everyone contributes scientific observations, inferences, limitations, tests and documentation.

## 11. Engineering and Research Principles

- Do not overengineer.
- Inspect existing code before implementing new functionality.
- Keep modules independent and reusable.
- Never commit large datasets directly to Git.
- Never commit credentials.
- Preserve raw data.
- Make experiments reproducible.
- Establish baseline statistics before cleaning.
- Measure the effect of each preprocessing transformation.
- Distinguish actual observations from assumptions.
- Do not fabricate experimental results.
- Include tests for important edge cases.
- Document linguistic limitations.
- Prioritize completing compulsory requirements before optional sandhi-aware processing.
