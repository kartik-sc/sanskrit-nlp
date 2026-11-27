"""
Unit tests for lexical analysis module.
"""

from collections import Counter
from pathlib import Path
import pytest

from src.analysis.lexical_analyzer import (
    compute_type_token_stats,
    compute_coverage,
    compute_zipf_parameters,
    analyze_text_corpus,
)


def test_type_token_stats_empty():
    counter = Counter()
    stats = compute_type_token_stats(counter)
    assert stats["tokens"] == 0
    assert stats["types"] == 0
    assert stats["type_token_ratio"] == 0.0
    assert stats["hapax_legomena"] == 0


def test_type_token_stats_basic():
    # 3 tokens, 2 types ('रामः': 2, 'गच्छति': 1)
    counter = Counter({"रामः": 2, "गच्छति": 1})
    stats = compute_type_token_stats(counter)

    assert stats["tokens"] == 3
    assert stats["types"] == 2
    assert pytest.approx(stats["type_token_ratio"], 0.001) == 2 / 3
    assert stats["hapax_legomena"] == 1  # 'गच्छति'
    assert pytest.approx(stats["hapax_type_percentage"], 0.01) == 50.0
    assert pytest.approx(stats["hapax_token_percentage"], 0.01) == 33.33
    assert stats["dis_legomena"] == 1  # 'रामः'


def test_coverage_calculation():
    # Frequencies: [50, 25, 15, 10] -> Total = 100 tokens, 4 types
    # Cumsum: [50, 75, 90, 100]
    freqs = [50, 25, 15, 10]
    total_tokens = 100
    total_types = 4

    cov = compute_coverage(freqs, total_tokens, total_types, thresholds=[0.25, 0.50, 0.75, 0.90, 0.99])

    # 25% threshold: 25 tokens reached at rank 1 (cumulative=50)
    assert cov["25%"]["types_required"] == 1
    assert cov["25%"]["tokens_accumulated"] == 50

    # 50% threshold: 50 tokens reached at rank 1 (cumulative=50)
    assert cov["50%"]["types_required"] == 1

    # 75% threshold: 75 tokens reached at rank 2 (cumulative=75)
    assert cov["75%"]["types_required"] == 2
    assert cov["75%"]["tokens_accumulated"] == 75

    # 90% threshold: 90 tokens reached at rank 3 (cumulative=90)
    assert cov["90%"]["types_required"] == 3

    # 99% threshold: 99 tokens reached at rank 4 (cumulative=100)
    assert cov["99%"]["types_required"] == 4


def test_zipf_parameters():
    # Ideal Zipf distribution for consecutive ranks 1..20: f(r) = 1000 // r
    freqs = [1000 // r for r in range(1, 21)]

    zipf = compute_zipf_parameters(freqs)
    # The exponent should be close to 1.0 and R^2 high
    assert pytest.approx(zipf["zipf_exponent_s"], 0.15) == 1.0
    assert zipf["r_squared"] > 0.95


def test_analyze_text_corpus(tmp_path: Path):
    sample_text = (
        "धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः ।\n"
        "मामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय ॥\n"
    )
    corpus_file = tmp_path / "sample_corpus.txt"
    corpus_file.write_text(sample_text, encoding="utf-8")

    res = analyze_text_corpus(corpus_file, name="Sample", top_n=5)
    tokens = sample_text.split()

    assert res["name"] == "Sample"
    assert res["summary"]["tokens"] == len(tokens)
    assert res["summary"]["types"] == len(set(tokens))
    assert len(res["top_words"]) <= 5
    assert "50%" in res["coverage"]
    assert "zipf_exponent_s" in res["zipf"]
