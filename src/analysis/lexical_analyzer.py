"""
Lexical Analysis Module for Sanskrit NLP.

Performs:
- Type-token analysis and Type-Token Ratio (TTR)
- Frequency distributions and rank tables
- Vocabulary coverage at 10%, 25%, 50%, 75%, 90%, 95%, and 99%
- Zipf's law regression (slope, intercept, R^2)
- Comparative analysis across Raw, Cleaned V1, and Cleaned V2 corpora
"""

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Configure Devanagari-compatible font if available
plt.rcParams["font.sans-serif"] = ["Nirmala UI", "DejaVu Sans", "Arial Unicode MS", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

COVERAGE_THRESHOLDS = [0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]


def compute_type_token_stats(counter: Counter) -> Dict[str, Any]:
    """Calculate core type-token statistics, TTR, and hapax legomena."""
    total_tokens = sum(counter.values())
    total_types = len(counter)
    ttr = (total_types / total_tokens) if total_tokens > 0 else 0.0

    # Hapax legomena (frequency == 1) & Dis legomena (frequency == 2)
    hapax_count = sum(1 for freq in counter.values() if freq == 1)
    dis_count = sum(1 for freq in counter.values() if freq == 2)

    hapax_type_pct = (hapax_count / total_types * 100) if total_types > 0 else 0.0
    hapax_token_pct = (hapax_count / total_tokens * 100) if total_tokens > 0 else 0.0

    return {
        "tokens": total_tokens,
        "types": total_types,
        "type_token_ratio": ttr,
        "ttr_percentage": round(ttr * 100, 2),
        "hapax_legomena": hapax_count,
        "hapax_type_percentage": round(hapax_type_pct, 2),
        "hapax_token_percentage": round(hapax_token_pct, 2),
        "dis_legomena": dis_count,
    }


def compute_coverage(
    sorted_freqs: List[int],
    total_tokens: int,
    total_types: int,
    thresholds: List[float] = COVERAGE_THRESHOLDS,
) -> Dict[str, Dict[str, Any]]:
    """
    Calculate the number of types required to cover specified cumulative
    token percentages (e.g. 10%, 25%, 50%, 75%, 90%, 95%, 99%).
    """
    if total_tokens == 0 or not sorted_freqs:
        return {
            f"{int(t * 100)}%": {
                "target_coverage": t,
                "types_required": 0,
                "type_percentage": 0.0,
                "tokens_accumulated": 0,
                "actual_coverage": 0.0,
            }
            for t in thresholds
        }

    cum_tokens = np.cumsum(sorted_freqs)
    coverage_results = {}

    for t in thresholds:
        target_tokens = t * total_tokens
        # Find first index where cumulative tokens >= target_tokens
        idx = int(np.searchsorted(cum_tokens, target_tokens))
        if idx >= len(sorted_freqs):
            idx = len(sorted_freqs) - 1

        types_needed = idx + 1
        actual_tokens = int(cum_tokens[idx])
        actual_cov = actual_tokens / total_tokens
        type_pct = (types_needed / total_types) * 100

        coverage_results[f"{int(round(t * 100))}%"] = {
            "target_coverage": t,
            "types_required": types_needed,
            "type_percentage": round(type_pct, 4),
            "tokens_accumulated": actual_tokens,
            "actual_coverage": round(actual_cov, 6),
        }

    return coverage_results


def compute_zipf_parameters(sorted_freqs: List[int]) -> Dict[str, Any]:
    """
    Fit log10(frequency) = log10(C) - s * log10(rank) to estimate
    Zipf exponent s and fit quality R^2.
    """
    if len(sorted_freqs) < 2:
        return {"slope": 0.0, "intercept": 0.0, "r_squared": 0.0, "alpha": 0.0}

    ranks = np.arange(1, len(sorted_freqs) + 1)
    log_ranks = np.log10(ranks)
    log_freqs = np.log10(sorted_freqs)

    # Linear regression: log(f) = a * log(r) + b, where a = -s
    slope, intercept = np.polyfit(log_ranks, log_freqs, deg=1)
    predicted = slope * log_ranks + intercept

    ss_res = np.sum((log_freqs - predicted) ** 2)
    ss_tot = np.sum((log_freqs - np.mean(log_freqs)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    return {
        "slope": round(float(slope), 4),
        "zipf_exponent_s": round(float(-slope), 4),
        "intercept": round(float(intercept), 4),
        "r_squared": round(float(r_squared), 4),
    }


def analyze_text_corpus(
    file_path: Path,
    name: str,
    top_n: int = 500,
    thresholds: List[float] = COVERAGE_THRESHOLDS,
) -> Dict[str, Any]:
    """
    Stream and analyze a plain text corpus file.
    Tokens are whitespace-delimited per shared project contract.
    """
    counter = Counter()

    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            tokens = line.split()
            if tokens:
                counter.update(tokens)

    stats = compute_type_token_stats(counter)
    total_tokens = stats["tokens"]
    total_types = stats["types"]

    # Sort descending by frequency; secondary alphabetical sort for deterministic ordering
    sorted_items = sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    sorted_freqs = [freq for _, freq in sorted_items]

    coverage = compute_coverage(sorted_freqs, total_tokens, total_types, thresholds)
    zipf = compute_zipf_parameters(sorted_freqs)

    # Top N words
    top_words = [
        {
            "rank": rank,
            "word": word,
            "frequency": freq,
            "percentage": round((freq / total_tokens * 100), 4) if total_tokens > 0 else 0.0,
        }
        for rank, (word, freq) in enumerate(sorted_items[:top_n], start=1)
    ]

    return {
        "name": name,
        "file_path": str(file_path),
        "summary": stats,
        "coverage": coverage,
        "zipf": zipf,
        "top_words": top_words,
        "_sorted_freqs": sorted_freqs,  # retained internally for plotting
    }


def generate_coverage_table(results: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
    """Generate comparative coverage DataFrame for CSV export."""
    rows = []
    threshold_keys = [f"{int(t * 100)}%" for t in COVERAGE_THRESHOLDS]

    for key in threshold_keys:
        row = {"Coverage Threshold": key}
        for name, res in results.items():
            cov = res["coverage"][key]
            row[f"{name} Types Needed"] = cov["types_required"]
            row[f"{name} % of Vocab"] = f"{cov['type_percentage']:.2f}%"
        rows.append(row)

    return pd.DataFrame(rows)


def generate_comparison_summary(results: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
    """Generate high-level comparative summary table."""
    rows = []
    for name, res in results.items():
        s = res["summary"]
        z = res["zipf"]
        c50 = res["coverage"]["50%"]
        c90 = res["coverage"]["90%"]
        rows.append({
            "Corpus": name,
            "Tokens": s["tokens"],
            "Types": s["types"],
            "TTR (%)": f"{s['ttr_percentage']:.2f}%",
            "Hapax Legomena (V1)": s["hapax_legomena"],
            "Hapax % of Types": f"{s['hapax_type_percentage']:.2f}%",
            "Types for 50% Coverage": c50["types_required"],
            "Types for 90% Coverage": c90["types_required"],
            "Zipf Exponent (s)": z["zipf_exponent_s"],
            "Zipf Fit (R^2)": z["r_squared"],
        })
    return pd.DataFrame(rows)


def plot_zipfs_law(results: Dict[str, Dict[str, Any]], output_path: Path) -> None:
    """Generate Zipf's law log-log plot comparing all corpora with reference line."""
    plt.figure(figsize=(10, 7), dpi=300)

    colors = {"Raw": "#e74c3c", "Cleaned V1": "#3498db", "Cleaned V2": "#2ecc71"}

    for name, res in results.items():
        freqs = res["_sorted_freqs"]
        ranks = np.arange(1, len(freqs) + 1)
        # Sample points logarithmically to reduce SVG/PNG density while keeping full curve fidelity
        if len(ranks) > 10000:
            indices = np.unique(np.round(np.geomspace(1, len(ranks), num=3000)).astype(int)) - 1
            sampled_ranks = ranks[indices]
            sampled_freqs = np.array(freqs)[indices]
        else:
            sampled_ranks = ranks
            sampled_freqs = freqs

        s = res["zipf"]["zipf_exponent_s"]
        r2 = res["zipf"]["r_squared"]
        label = f"{name} (s = {s:.2f}, $R^2$ = {r2:.3f})"
        plt.loglog(
            sampled_ranks,
            sampled_freqs,
            label=label,
            color=colors.get(name, "black"),
            alpha=0.8,
            linewidth=1.8,
        )

    # Reference theoretical Zipf line s = 1.0 based on top frequency of Cleaned V2
    max_f = results.get("Cleaned V2", list(results.values())[0])["_sorted_freqs"][0]
    ref_ranks = np.array([1, 100_000])
    ref_freqs = max_f / ref_ranks
    plt.loglog(
        ref_ranks,
        ref_freqs,
        label="Ideal Zipfian ($f \\propto 1/r$)",
        color="#34495e",
        linestyle="--",
        linewidth=1.5,
        alpha=0.7,
    )

    plt.title("Zipf's Law Log-Log Rank vs. Frequency Distribution (Sanskrit Corpora)", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Log10 Rank ($r$)", fontsize=11)
    plt.ylabel("Log10 Frequency ($f$)", fontsize=11)
    plt.grid(True, which="both", linestyle=":", alpha=0.6)
    plt.legend(fontsize=10, loc="upper right", framealpha=0.95)
    plt.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_vocabulary_coverage(results: Dict[str, Dict[str, Any]], output_path: Path) -> None:
    """Generate cumulative vocabulary coverage curves comparing all corpora."""
    plt.figure(figsize=(10, 7), dpi=300)

    colors = {"Raw": "#e74c3c", "Cleaned V1": "#3498db", "Cleaned V2": "#2ecc71"}

    for name, res in results.items():
        freqs = res["_sorted_freqs"]
        total_tokens = res["summary"]["tokens"]
        cum_tokens = np.cumsum(freqs)
        cum_coverage_pct = (cum_tokens / total_tokens) * 100
        ranks = np.arange(1, len(freqs) + 1)

        # Sample for plotting efficiency
        if len(ranks) > 10000:
            indices = np.unique(np.round(np.geomspace(1, len(ranks), num=3000)).astype(int)) - 1
            sampled_ranks = ranks[indices]
            sampled_cov = cum_coverage_pct[indices]
        else:
            sampled_ranks = ranks
            sampled_cov = cum_coverage_pct

        plt.plot(
            sampled_ranks,
            sampled_cov,
            label=f"{name} (Tokens: {total_tokens:,})",
            color=colors.get(name, "black"),
            linewidth=2.0,
        )

    # Highlight key thresholds: 50%, 75%, 90%, 95%
    for thresh in [50, 75, 90, 95]:
        plt.axhline(y=thresh, color="gray", linestyle="--", alpha=0.4, linewidth=0.8)
        plt.text(10, thresh + 0.8, f"{thresh}% coverage", color="#555", fontsize=8)

    plt.xscale("log")
    plt.title("Cumulative Vocabulary Coverage Curve (Sanskrit Corpora)", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Vocabulary Types (Rank in log scale)", fontsize=11)
    plt.ylabel("Cumulative Token Coverage (%)", fontsize=11)
    plt.ylim(0, 102)
    plt.grid(True, which="both", linestyle=":", alpha=0.6)
    plt.legend(fontsize=10, loc="lower right", framealpha=0.95)
    plt.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_top_words_comparison(results: Dict[str, Dict[str, Any]], output_path: Path, top_k: int = 15) -> None:
    """Generate bar chart comparing top words across V1 and V2."""
    v1_words = {item["word"]: item["frequency"] for item in results["Cleaned V1"]["top_words"][:top_k]}
    v2_words = {item["word"]: item["frequency"] for item in results["Cleaned V2"]["top_words"][:top_k]}

    # Union of top words
    words = list(dict.fromkeys(list(v2_words.keys())[:top_k]))
    v1_freqs = [v1_words.get(w, 0) for w in words]
    v2_freqs = [v2_words.get(w, 0) for w in words]

    x = np.arange(len(words))
    width = 0.38

    plt.figure(figsize=(12, 6), dpi=300)
    plt.bar(x - width / 2, v1_freqs, width, label="Cleaned V1", color="#3498db")
    plt.bar(x + width / 2, v2_freqs, width, label="Cleaned V2", color="#2ecc71")

    plt.xlabel("Word Types", fontsize=11)
    plt.ylabel("Frequency", fontsize=11)
    plt.title(f"Top {top_k} Words Comparison: Cleaned V1 vs. Cleaned V2", fontsize=13, fontweight="bold", pad=12)
    plt.xticks(x, words, rotation=45, ha="right", fontsize=10)
    plt.grid(axis="y", linestyle=":", alpha=0.6)
    plt.legend(fontsize=10)
    plt.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Run Lexical Analysis on Sanskrit Corpora")
    parser.add_argument("--raw", default="data/interim/working_1m.txt", help="Path to raw corpus text")
    parser.add_argument("--v1", default="data/processed/clean_corpus.txt", help="Path to Cleaned V1 corpus text")
    parser.add_argument("--v2", default="data/processed/clean_corpus_v2.txt", help="Path to Cleaned V2 corpus text")
    parser.add_argument("--metrics-out", default="results/metrics/lexical_analysis.json", help="Output path for metrics JSON")
    parser.add_argument("--tables-dir", default="results/tables", help="Directory for CSV tables")
    parser.add_argument("--plots-dir", default="results/plots", help="Directory for PNG plots")
    args = parser.parse_args()

    corpora_specs = [
        ("Raw", Path(args.raw)),
        ("Cleaned V1", Path(args.v1)),
        ("Cleaned V2", Path(args.v2)),
    ]

    results = {}
    for name, path in corpora_specs:
        if not path.exists():
            raise FileNotFoundError(f"Corpus file not found: {path}")
        print(f"Analyzing {name} corpus ({path})...", flush=True)
        results[name] = analyze_text_corpus(path, name=name)

    tables_dir = Path(args.tables_dir)
    plots_dir = Path(args.plots_dir)
    tables_dir.mkdir(parents=True, exist_ok=True)
    plots_dir.mkdir(parents=True, exist_ok=True)

    # 1. Save Summary CSV & Coverage CSV
    summary_df = generate_comparison_summary(results)
    summary_csv_path = tables_dir / "corpus_comparison.csv"
    summary_df.to_csv(summary_csv_path, index=False, encoding="utf-8")
    print(f"Saved summary comparison table to {summary_csv_path}")

    coverage_df = generate_coverage_table(results)
    coverage_csv_path = tables_dir / "vocabulary_coverage.csv"
    coverage_df.to_csv(coverage_csv_path, index=False, encoding="utf-8")
    print(f"Saved vocabulary coverage table to {coverage_csv_path}")

    # 2. Save individual top frequency tables
    for name, res in results.items():
        slug = name.lower().replace(" ", "_")
        top_df = pd.DataFrame(res["top_words"][:500])
        csv_path = tables_dir / f"frequency_top500_{slug}.csv"
        top_df.to_csv(csv_path, index=False, encoding="utf-8")
        print(f"Saved top 500 frequencies for {name} to {csv_path}")

    # 3. Save comparative top 50 table
    v2_top50 = results["Cleaned V2"]["top_words"][:50]
    top50_comparison_rows = []
    v1_map = {item["word"]: (item["rank"], item["frequency"]) for item in results["Cleaned V1"]["top_words"]}
    raw_map = {item["word"]: (item["rank"], item["frequency"]) for item in results["Raw"]["top_words"]}

    for item in v2_top50:
        w = item["word"]
        v2_rank, v2_f = item["rank"], item["frequency"]
        v1_rank, v1_f = v1_map.get(w, ("N/A", 0))
        raw_rank, raw_f = raw_map.get(w, ("N/A", 0))
        top50_comparison_rows.append({
            "V2 Rank": v2_rank,
            "Word": w,
            "V2 Frequency": v2_f,
            "V1 Rank": v1_rank,
            "V1 Frequency": v1_f,
            "Raw Rank": raw_rank,
            "Raw Frequency": raw_f,
        })
    top50_comp_df = pd.DataFrame(top50_comparison_rows)
    top50_comp_path = tables_dir / "top50_words_comparison.csv"
    top50_comp_df.to_csv(top50_comp_path, index=False, encoding="utf-8")
    print(f"Saved top 50 comparison table to {top50_comp_path}")

    # 4. Generate Visualizations
    zipf_plot_path = plots_dir / "zipfs_law.png"
    plot_zipfs_law(results, zipf_plot_path)
    print(f"Saved Zipf's Law plot to {zipf_plot_path}")

    cov_plot_path = plots_dir / "vocabulary_coverage.png"
    plot_vocabulary_coverage(results, cov_plot_path)
    print(f"Saved Vocabulary Coverage plot to {cov_plot_path}")

    top_plot_path = plots_dir / "top_words_comparison.png"
    plot_top_words_comparison(results, top_plot_path)
    print(f"Saved Top Words comparison plot to {top_plot_path}")

    # 5. Save JSON metrics (remove internal _sorted_freqs arrays to keep JSON clean and lightweight)
    json_metrics = {}
    for name, res in results.items():
        res_copy = dict(res)
        res_copy.pop("_sorted_freqs", None)
        json_metrics[name] = res_copy

    metrics_out_path = Path(args.metrics_out)
    metrics_out_path.parent.mkdir(parents=True, exist_ok=True)
    with metrics_out_path.open("w", encoding="utf-8") as f:
        json.dump(json_metrics, f, indent=2, ensure_ascii=False)
    print(f"Saved comprehensive metrics JSON to {metrics_out_path}")

    print("\n--- Summary Comparison Table ---")
    print(summary_df.to_string(index=False))
    print("\n--- Vocabulary Coverage Table ---")
    print(coverage_df.to_string(index=False))


if __name__ == "__main__":
    main()
