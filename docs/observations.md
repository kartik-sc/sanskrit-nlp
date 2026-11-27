# Scientific Observations & Lexical Analysis Findings

## 1. Executive Summary

This study conducted comprehensive lexical and statistical analysis across three stages of a 1,000,000-token Sanskrit corpus acquired from AI4Bharat Sangraha:
1. **Raw Interim Corpus (`working_1m.txt`)**
2. **Cleaned Corpus V1 (`clean_corpus.txt`)**
3. **Cleaned Corpus V2 with Vedic Accent & Compound Recovery (`clean_corpus_v2.txt`)**

Our findings reveal profound quantitative characteristics of Sanskrit morphology, quantify the distortive effect of uncleaned textual noise on statistical laws, and demonstrate the effectiveness of refined linguistic preprocessing (V2).

---

## 2. Quantitative Corpus Comparison

| Metric | Raw Corpus | Cleaned V1 | Cleaned V2 | Δ (V2 vs V1) | Δ (V2 vs Raw) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Total Tokens ($N$)** | 1,000,256 | 793,768 | 803,139 | +9,371 (+1.18%) | -197,117 (-19.71%) |
| **Unique Types ($V$)** | 436,105 | 392,955 | 398,164 | +5,209 (+1.33%) | -37,941 (-8.70%) |
| **Type-Token Ratio (TTR)** | **43.60%** | **49.51%** | **49.58%** | +0.07% | +5.98% |
| **Hapax Legomena ($V_1$)** | 375,452 | 336,431 | 340,964 | +4,533 | -34,488 |
| **Hapax % of Vocabulary** | **86.09%** | **85.62%** | **85.63%** | +0.01% | -0.46% |
| **Hapax % of Total Tokens** | 37.54% | 42.38% | 42.45% | +0.07% | +4.91% |
| **Dis Legomena ($V_2$)** | 28,958 | 27,243 | 27,558 | +315 | -1,400 |
| **Zipf Exponent ($s$)** | 0.4543 | 0.4626 | 0.4622 | -0.0004 | +0.0079 |
| **Zipf Goodness of Fit ($R^2$)**| 0.7375 | 0.7474 | 0.7471 | -0.0003 | +0.0096 |

---

## 3. Vocabulary Coverage Analysis

Vocabulary coverage quantifies the cumulative proportion of running text (tokens) accounted for by the most frequent unique words (types).

| Coverage Threshold | Raw Types Needed | Raw % of Vocab | Cleaned V1 Types | Cleaned V1 % of Vocab | Cleaned V2 Types | Cleaned V2 % of Vocab |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **10%** | 2 | 0.00% | 25 | 0.01% | 25 | 0.01% |
| **25%** | 90 | 0.02% | 797 | 0.20% | 816 | 0.20% |
| **50%** | 12,416 | 2.85% | 26,924 | 6.85% | 27,430 | 6.89% |
| **75%** | 186,041 | 42.66% | 194,513 | 49.50% | 197,380 | 49.57% |
| **90%** | 336,080 | 77.06% | 313,579 | 79.80% | 317,851 | 79.83% |
| **95%** | 386,093 | 88.53% | 353,267 | 89.90% | 358,008 | 89.91% |
| **99%** | 426,103 | 97.71% | 385,018 | 97.98% | 390,133 | 97.98% |

---

## 4. Most Frequent Words (Top 25)

The table below contrasts word ranks across Cleaned V2, Cleaned V1, and Raw:

| V2 Rank | Word Form | V2 Freq | V2 Token % | V1 Rank | V1 Freq | Raw Rank | Raw Freq | Grammatical Category |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | इति | 13,630 | 1.70% | 1 | 13,605 | 3 | 13,181 | Avyaya (quotative particle) |
| **2** | न | 11,896 | 1.48% | 2 | 11,860 | 4 | 11,488 | Avyaya (negative particle) |
| **3** | च | 10,894 | 1.36% | 3 | 10,871 | 5 | 10,472 | Avyaya (conjunctive "and") |
| **4** | वा | 4,284 | 0.53% | 4 | 4,276 | 7 | 3,964 | Avyaya (disjunctive "or") |
| **5** | तु | 3,862 | 0.48% | 5 | 3,856 | 9 | 3,808 | Avyaya (adversative "but/indeed") |
| **6** | एव | 3,230 | 0.40% | 6 | 3,227 | 10 | 3,077 | Avyaya (emphatic "alone/only") |
| **7** | तथा | 3,130 | 0.39% | 7 | 3,125 | 11 | 3,046 | Avyaya (correlative "thus/so") |
| **8** | स | 3,079 | 0.38% | 8 | 3,059 | 12 | 2,951 | Pronoun (tad, masc. nom. sing.) |
| **9** | हि | 2,562 | 0.32% | 9 | 2,548 | 15 | 2,493 | Avyaya (causal "for/because") |
| **10** | तत्र | 2,400 | 0.30% | 10 | 2,391 | 16 | 2,347 | Avyaya (locative adverb "there") |
| **11** | भवति | 2,235 | 0.28% | 11 | 2,231 | 18 | 1,859 | Verb (√bhū, pr. act. 3rd sing.) |
| **12** | एवं | 2,162 | 0.27% | 12 | 2,158 | 17 | 2,137 | Avyaya (manner adverb "thus") |
| **13** | यथा | 1,783 | 0.22% | 13 | 1,764 | 21 | 1,665 | Avyaya (relative "as/just as") |
| **14** | तस्य | 1,740 | 0.22% | 14 | 1,735 | 19 | 1,695 | Pronoun (tad, gen. sing.) |
| **15** | ते | 1,657 | 0.21% | 15 | 1,652 | 23 | 1,591 | Pronoun (tad nom. pl. / yushmad dat/gen) |
| **16** | भावः | 1,557 | 0.19% | 16 | 1,554 | 24 | 1,478 | Noun (masc. nom. sing.) |
| **17** | स्यात् | 1,315 | 0.16% | 17 | 1,311 | 31 | 1,102 | Verb (√as, optative 3rd sing.) |
| **18** | किं | 1,304 | 0.16% | 18 | 1,302 | 27 | 1,270 | Pronoun (interrogative "what/why") |
| **19** | अथ | 1,216 | 0.15% | 19 | 1,211 | 30 | 1,151 | Avyaya (auspicious / topic shift) |
| **20** | तेन | 1,190 | 0.15% | 20 | 1,189 | 29 | 1,163 | Pronoun (tad instrumental sing.) |

*Note on Raw ranks 1 and 2:* In the uncleaned Raw corpus, Rank 1 was the single danda `।` (88,319 occurrences, 8.83% of all tokens) and Rank 2 was the double danda `॥` (23,535 occurrences, 2.35% of all tokens). Over 11% of the raw corpus consisted solely of verse and sentence delimiter marks.

---

## 5. Key Scientific Observations and Inferences

### Observation 1: Exceptionally High Type-Token Ratio (~49.6%)
- **Data**: Sanskrit exhibits a TTR of **49.58%** on an 800K-token corpus, meaning roughly 1 out of every 2 tokens encountered is a distinct surface form.
- **Linguistic Inference**: In comparison to analytic languages like English (where 1M tokens yields a TTR of roughly 2%–5%), Sanskrit is a synthetic, highly inflected,fusional language. Every nominal stem produces up to 24 distinct case-number paradigm forms (*vibhakti*), verbal roots conjugate across 10 tenses/moods (*lakāra*) across two voices (*parasmaipada* and *ātmanepada*), and prefixes (*upasarga*) create distinct lexical derivations. This morphological productivity directly suppresses token repetition and inflates vocabulary type count.

### Observation 2: Extreme Hapax Legomena Dominance (85.6% of Vocabulary)
- **Data**: 340,964 out of 398,164 unique types in Cleaned V2 (**85.63%**) appear exactly once in the corpus (*hapax legomena*). Words occurring once or twice (*hapax* + *dis legomena*) account for **92.55%** of the entire vocabulary.
- **Linguistic Inference**: Sanskrit possesses productive compounding (*samāsa*). Complex nominal compounds (Tatpuruṣa, Bahuvrīhi, Dvandva) create ad-hoc multi-word semantic units written without internal whitespace. Because each authorial compound can combine two, three, or more stems into a unique surface token, compounding continuously feeds an extraordinarily heavy long tail of hapax legomena.

### Observation 3: Severe Flattening of Zipf's Law ($s \approx 0.46$)
- **Data**: Fitting the Zipfian power law $\log_{10}(f) = \log_{10}(C) - s \cdot \log_{10}(r)$ yields an empirical exponent $s = 0.4622$ ($R^2 = 0.7471$), which deviates substantially from the canonical Zipfian exponent $s \approx 1.0$.
- **Linguistic Inference**: 
  1. **Low Head Mass**: The most frequent word in Sanskrit (`इति`) accounts for only **1.70%** of the corpus. In English, the most frequent word ("the") typically occupies 6% to 7% of all tokens.
  2. **Thick Tail**: Because inflected variants and compounds dilute token concentrations, the frequency drops much more slowly as rank increases, resulting in a significantly flatter log-log slope ($s \approx 0.46$). Sanskrit textual corpora exhibit what is termed a "super-heavy tail" distribution.

### Observation 4: Vocabulary Coverage Resistance
- **Data**: Reaching 50% corpus coverage requires **27,430 unique types** (6.89% of vocabulary). Reaching 90% coverage requires **317,851 types** (79.83% of vocabulary). Reaching 95% requires **358,008 types** (89.91% of vocabulary).
- **Linguistic Inference**: In English, a lexicon of ~1,000 words commonly covers 70%–75% of running text. In Sanskrit, 1,000 words cover only ~27% of running text. For downstream NLP tasks (Phase 2 language models and embeddings), standard whitespace-delimited subword tokenization without morphological segmentation (*sandhi* splitting) will suffer from catastrophic out-of-vocabulary (OOV) rates. Morphological segmentation and subword tokenizers (BPE/WordPiece) are linguistically mandatory for Sanskrit.

### Observation 5: Preprocessing Distortions in Raw Data
- **Data**: In the Raw corpus, 50% coverage appeared to require only 12,416 types (versus 27,430 in V2), and 10% coverage required just 2 types (`।` and `॥`).
- **Methodological Inference**: Noise tokens (punctuation, ASCII artifacts, isolated numbers) masqueraded as high-frequency "lexical" items, artificially steepening the head of the curve and creating an illusion of high coverage. Strict cleaning (V1) and targeted recovery (V2) properly expose the true linguistic complexity of the vocabulary.

### Observation 6: Efficacy of Refined Cleaning (V2 vs V1)
- **Data**: V2 recovered **9,371 tokens** and **5,209 unique types** compared to V1 while maintaining clean lexical validity.
- **Inference**: V1's aggressive deletion of tokens containing punctuation discarded legitimate Vedic accented literature (e.g., `तस्मा॑त्`) and hyphenated Sanskrit compounds (e.g., `जैमिनीय-संहिता-पाठविशेषाः`). V2 restored these forms through Unicode combining mark preservation and hyphen-boundary token splitting, proving that linguistic domain knowledge is essential during data engineering.

---

## 6. Generated Visualizations and Artifacts

All artifacts have been programmatically generated and saved to the project directory:
- **Zipf's Law Plot**: `results/plots/zipfs_law.png`
- **Vocabulary Coverage Curves**: `results/plots/vocabulary_coverage.png`
- **Top Words Comparison Bar Chart**: `results/plots/top_words_comparison.png`
- **Comprehensive Metrics JSON**: `results/metrics/lexical_analysis.json`
- **Full Frequency & Coverage Tables**: `results/tables/`
