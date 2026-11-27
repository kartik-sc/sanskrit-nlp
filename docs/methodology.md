# Lexical Analysis Methodology

## 1. Overview and Scope

Lexical Analysis (Phase 1, Requirements 3, 4, 5, 6, 7, and 9) provides quantitative profiling of lexical diversity, word-frequency distributions, vocabulary saturation, and compliance with statistical language laws across three iterations of the Sanskrit corpus:
- **Raw Corpus**: `data/interim/working_1m.txt`
- **Cleaned Corpus V1**: `data/processed/clean_corpus.txt`
- **Cleaned Corpus V2**: `data/processed/clean_corpus_v2.txt`

Analysis operates strictly on plain UTF-8 text with whitespace-delimited tokens per the project data contract.

---

## 2. Mathematical Formulations

### 2.1 Type-Token Ratio (TTR)
Let $N$ denote the total number of running word tokens in the corpus, and let $V$ denote the vocabulary size (cardinality of the set of unique types):

$$N = \sum_{w \in V} f(w)$$

$$V = |\{w : f(w) \ge 1\}|$$

The Type-Token Ratio is defined as:

$$\text{TTR} = \frac{V}{N}$$

### 2.2 Hapax Legomena & Dis Legomena
Hapax legomena ($V_1$) are word types occurring with frequency exactly 1:

$$V_1 = |\{w \in V : f(w) = 1\}|$$

The vocabulary hapax ratio is:

$$H_V = \frac{V_1}{V}$$

Dis legomena ($V_2$) are word types occurring with frequency exactly 2:

$$V_2 = |\{w \in V : f(w) = 2\}|$$

### 2.3 Cumulative Vocabulary Coverage
Word types are sorted descending by frequency:

$$f(w_1) \ge f(w_2) \ge \dots \ge f(w_V)$$

Ties in frequency are resolved alphabetically to maintain deterministic rank assignment. The cumulative token count at rank $k$ is:

$$C(k) = \sum_{i=1}^k f(w_i)$$

The vocabulary coverage fraction at rank $k$ is:

$$\text{Cov}(k) = \frac{C(k)}{N}$$

For target coverage threshold $\tau \in \{0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99\}$, the minimum types required $k_\tau$ is:

$$k_\tau = \min \{k : \text{Cov}(k) \ge \tau\}$$

### 2.4 Zipf's Law Regression
According to Zipf's law, the frequency $f$ of a word type is inversely proportional to its rank $r$:

$$f(r) \approx \frac{C}{r^s}$$

Taking the base-10 logarithm of both sides transforms this into a linear relationship:

$$\log_{10}(f) = \log_{10}(C) - s \cdot \log_{10}(r)$$

Using ordinary least squares (OLS) linear regression on the empirical pairs $(\log_{10}(r), \log_{10}(f))$:
- **Slope**: $\beta = -s \implies s = -\beta$
- **Intercept**: $\alpha = \log_{10}(C)$
- **Coefficient of Determination ($R^2$)**:

$$R^2 = 1 - \frac{\sum_{i=1}^V (\log_{10} f_i - \hat{y}_i)^2}{\sum_{i=1}^V (\log_{10} f_i - \bar{y})^2}$$

---

## 3. Implementation Architecture

The lexical analysis pipeline is implemented in `src/analysis/lexical_analyzer.py`:
- **Streaming Tokenizer**: Processes text line-by-line using Python's native `split()`, maintaining $O(V)$ memory efficiency without loading entire 22 MB files into flat lists.
- **Counter Accumulator**: Tracks frequencies using `collections.Counter`.
- **Searchsorted Optimization**: Computes coverage thresholds using vectorized `np.searchsorted` over `np.cumsum`, executing coverage calculation in $O(V)$ time.
- **Logarithmic Downsampling for Plotting**: In datasets with $V \approx 400,000$ points, plotting all points can cause excessive image file sizes or rendering lag. The plotting module utilizes `np.geomspace` to log-sample 3,000 points spanning ranks $1$ to $400,000$, ensuring visual accuracy while keeping vector rendering lightweight.
- **Devanagari Font Binding**: Dynamically binds Windows native `Nirmala UI` font to prevent Unicode glyph omissions in Matplotlib.

---

## 4. Execution Command

To run the complete lexical pipeline and regenerate all metrics, tables, and plots:

```bash
python src/analysis/lexical_analyzer.py \
  --raw data/interim/working_1m.txt \
  --v1 data/processed/clean_corpus.txt \
  --v2 data/processed/clean_corpus_v2.txt \
  --metrics-out results/metrics/lexical_analysis.json \
  --tables-dir results/tables \
  --plots-dir results/plots
```

To run the automated test suite:

```bash
python -m pytest tests/test_lexical_analysis.py -v
```
