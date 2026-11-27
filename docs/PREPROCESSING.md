# Sanskrit Corpus Acquisition and Preprocessing

## 1. Objective

Acquire, validate and preprocess a large Sanskrit corpus for reproducible statistical and linguistic analysis.

## 2. Dataset

- Source: AI4Bharat Sangraha
- Subset: verified/san
- Revision: 8b813c3f62d37b2fa174d68c31e8b35ae2fe85e8
- Sampling: Sequential
- Records: 1,971
- Original whitespace tokens: 1,000,256
- PDF records: 1,845
- Web records: 126
- Encoding: UTF-8
- Line endings: LF

The original JSONL records and extracted plain-text corpus are preserved separately and versioned using DVC and DagsHub.

## 3. Initial Data-Quality Profiling

The raw corpus contained 436,105 unique whitespace-delimited token forms, yielding a type-token ratio of 43.60%.

Identified issues included:

- 141,282 punctuation-only tokens.
- 19,564 numeric-only tokens.
- 35,841 tokens containing numbers.
- 20,490 tokens containing Latin characters.
- 472 mixed Devanagari-Latin tokens.
- OCR errors, broken words and editorial annotations.
- Possible non-Sanskrit quotations.

Noise categories overlap and must not be summed directly.

No exact duplicate records or duplicate document identifiers were detected.

## 4. Cleaning V1

The initial preprocessing pipeline performed:

- Unicode NFC normalization.
- Whitespace and line-ending normalization.
- Unwanted control-character removal.
- Removal of punctuation-only tokens.
- Stripping of surrounding punctuation.
- Filtering of numeric and Latin-containing tokens.
- Devanagari letter and combining-mark validation.

A separate normalized JSONL corpus was retained for sentence segmentation.

V1 produced 793,768 lexical tokens and 392,955 unique types. A total of 206,488 original whitespace tokens were removed.

## 5. Error Analysis

Inspection of rejected tokens revealed that V1 discarded potentially valid linguistic content containing:

- Vedic accent marks.
- Hyphens separating Sanskrit words.
- Other selected internal punctuation.

Examples included तस्मा॑त् and जैमिनीय-संहिता-पाठविशेषाः.

These findings motivated a targeted refinement.

## 6. Cleaning V2

V2 introduced:

- Support for Vedic accent marks and selected Vedic combining characters.
- Recovery of valid Devanagari components separated by selected punctuation.
- Continued rejection of numeric and Latin-contaminated tokens.
- Preservation of Sanskrit avagraha and existing compound forms.

V2 retained 2,070 Vedic-marked tokens and recovered 3,409 punctuation-separated input tokens, yielding 7,301 output tokens from splitting.

## 7. Comparative Results

| Metric           |       Raw |      V1 |      V2 |
| ---------------- | --------: | ------: | ------: |
| Tokens           | 1,000,256 | 793,768 | 803,139 |
| Unique types     |   436,105 | 392,955 | 398,164 |
| Type-token ratio |    43.60% |  49.51% |  49.58% |

V2 yielded a net increase of 9,371 tokens and 5,209 unique types relative to V1.

## 8. Observations and Inferences

- Punctuation constituted a substantial proportion of the original whitespace tokens.
- Removing frequently occurring punctuation reduced corpus size more proportionally than vocabulary size, increasing TTR.
- Unicode and whitespace normalization did not change aggregate type-token statistics.
- Strict script filtering discarded valid Vedic-marked forms.
- Targeted refinements improved linguistic content retention.
- Devanagari script membership alone does not establish Sanskrit language membership.
- Higher vocabulary size or TTR does not independently establish corpus quality.

## 9. Limitations

- Sequential sampling may introduce source and genre bias.
- The corpus is predominantly PDF-derived.
- OCR errors and incorrectly separated words remain.
- Script-based filtering cannot reliably identify other Devanagari languages.
- Internal punctuation splitting is heuristic and may fragment legitimate constructions.
- Valid Sanskrit content containing numbers or Latin OCR substitutions may be discarded.
- Sandhi splitting, lemmatization and automatic OCR correction are outside the current scope.
- V2 is a filtered lexical representation, not a linguistically perfect Sanskrit corpus.

## 10. Final Dataset Handoff

- Raw records: data/raw/working_1m.jsonl
- Raw plain text: data/interim/working_1m.txt
- Normalized records: data/processed/normalized_corpus.jsonl
- Sentence-ready text: data/processed/sentence_ready.txt
- Strict lexical corpus: data/processed/clean_corpus.txt
- Final lexical corpus: data/processed/clean_corpus_v2.txt

V2 is recommended for final lexical analysis. Normalized JSONL is recommended for sentence segmentation because it preserves punctuation and record boundaries.

All original and intermediate representations are retained for reproducibility and comparative analysis.
