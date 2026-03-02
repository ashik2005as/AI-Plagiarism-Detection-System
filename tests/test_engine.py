"""Unit tests for plagiarism_engine.py."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from plagiarism_engine import (
    calculate_similarity,
    classify_plagiarism_level,
    compare_documents,
    compare_multiple_documents,
    get_sentence_matches,
)


IDENTICAL_TEXT = (
    "Machine learning is a subset of artificial intelligence. "
    "It enables computers to learn from data without being explicitly programmed."
)

SIMILAR_TEXT = (
    "Machine learning is part of artificial intelligence. "
    "Computers can learn from data without explicit programming."
)

DIFFERENT_TEXT = (
    "The rain in Spain stays mainly in the plain. "
    "Peter Piper picked a peck of pickled peppers."
)


class TestClassifyPlagiarismLevel:
    """Tests for classify_plagiarism_level()."""

    def test_low(self):
        assert classify_plagiarism_level(0) == "Low"
        assert classify_plagiarism_level(15) == "Low"
        assert classify_plagiarism_level(29.9) == "Low"

    def test_medium(self):
        assert classify_plagiarism_level(30) == "Medium"
        assert classify_plagiarism_level(50) == "Medium"
        assert classify_plagiarism_level(69.9) == "Medium"

    def test_high(self):
        assert classify_plagiarism_level(70) == "High"
        assert classify_plagiarism_level(85) == "High"
        assert classify_plagiarism_level(100) == "High"


class TestCalculateSimilarity:
    """Tests for calculate_similarity()."""

    def test_identical_texts_have_high_similarity(self):
        score = calculate_similarity(IDENTICAL_TEXT, IDENTICAL_TEXT)
        assert score > 0.95

    def test_similar_texts_have_moderate_similarity(self):
        score = calculate_similarity(IDENTICAL_TEXT, SIMILAR_TEXT)
        assert score > 0.3

    def test_different_texts_have_low_similarity(self):
        score = calculate_similarity(IDENTICAL_TEXT, DIFFERENT_TEXT)
        assert score < 0.5

    def test_empty_text1_returns_zero(self):
        assert calculate_similarity("", IDENTICAL_TEXT) == 0.0

    def test_empty_text2_returns_zero(self):
        assert calculate_similarity(IDENTICAL_TEXT, "") == 0.0

    def test_both_empty_returns_zero(self):
        assert calculate_similarity("", "") == 0.0

    def test_returns_float(self):
        score = calculate_similarity(IDENTICAL_TEXT, SIMILAR_TEXT)
        assert isinstance(score, float)

    def test_score_in_range(self):
        score = calculate_similarity(IDENTICAL_TEXT, SIMILAR_TEXT)
        assert 0.0 <= score <= 1.0


class TestGetSentenceMatches:
    """Tests for get_sentence_matches()."""

    def test_returns_list(self):
        matches = get_sentence_matches(IDENTICAL_TEXT, SIMILAR_TEXT)
        assert isinstance(matches, list)

    def test_matches_have_required_keys(self):
        matches = get_sentence_matches(IDENTICAL_TEXT, SIMILAR_TEXT)
        for match in matches:
            assert "sentence1" in match
            assert "sentence2" in match
            assert "similarity" in match

    def test_similarity_values_in_range(self):
        matches = get_sentence_matches(IDENTICAL_TEXT, SIMILAR_TEXT)
        for match in matches:
            assert 0.0 <= match["similarity"] <= 1.0

    def test_sorted_descending(self):
        matches = get_sentence_matches(IDENTICAL_TEXT, SIMILAR_TEXT)
        scores = [m["similarity"] for m in matches]
        assert scores == sorted(scores, reverse=True)

    def test_empty_inputs(self):
        assert get_sentence_matches("", IDENTICAL_TEXT) == []
        assert get_sentence_matches(IDENTICAL_TEXT, "") == []

    def test_top_n_respected(self):
        matches = get_sentence_matches(IDENTICAL_TEXT, SIMILAR_TEXT, top_n=2)
        assert len(matches) <= 2


class TestCompareDocuments:
    """Tests for compare_documents()."""

    def test_result_keys_present(self):
        result = compare_documents(IDENTICAL_TEXT, SIMILAR_TEXT)
        assert "similarity_percentage" in result
        assert "plagiarism_level" in result
        assert "sentence_matches" in result

    def test_similarity_percentage_range(self):
        result = compare_documents(IDENTICAL_TEXT, SIMILAR_TEXT)
        assert 0.0 <= result["similarity_percentage"] <= 100.0

    def test_high_similarity_for_identical(self):
        result = compare_documents(IDENTICAL_TEXT, IDENTICAL_TEXT)
        assert result["similarity_percentage"] > 70
        assert result["plagiarism_level"] == "High"

    def test_low_similarity_for_different(self):
        result = compare_documents(IDENTICAL_TEXT, DIFFERENT_TEXT)
        # Different documents should have a lower level
        assert result["plagiarism_level"] in ("Low", "Medium")


class TestCompareMultipleDocuments:
    """Tests for compare_multiple_documents()."""

    def test_requires_at_least_two(self):
        with pytest.raises(ValueError):
            compare_multiple_documents(["only one document here"])

    def test_returns_square_matrix(self):
        texts = [IDENTICAL_TEXT, SIMILAR_TEXT, DIFFERENT_TEXT]
        result = compare_multiple_documents(texts)
        n = result["document_count"]
        assert n == 3
        assert len(result["similarity_matrix"]) == n
        for row in result["similarity_matrix"]:
            assert len(row) == n

    def test_diagonal_is_100(self):
        texts = [IDENTICAL_TEXT, SIMILAR_TEXT]
        result = compare_multiple_documents(texts)
        for i in range(result["document_count"]):
            assert result["similarity_matrix"][i][i] == 100.0

    def test_values_in_range(self):
        texts = [IDENTICAL_TEXT, SIMILAR_TEXT, DIFFERENT_TEXT]
        result = compare_multiple_documents(texts)
        for row in result["similarity_matrix"]:
            for val in row:
                assert 0.0 <= val <= 100.0
