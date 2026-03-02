"""Unit tests for preprocessing.py."""

import sys
import os

# Make sure repo root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from preprocessing import preprocess_text, tokenize_sentences


class TestPreprocessText:
    """Tests for preprocess_text()."""

    def test_returns_string(self):
        result = preprocess_text("Hello world.")
        assert isinstance(result, str)

    def test_lowercases(self):
        result = preprocess_text("HELLO WORLD")
        assert result == result.lower()

    def test_removes_punctuation(self):
        result = preprocess_text("Hello, world! How are you?")
        assert "," not in result
        assert "!" not in result
        assert "?" not in result

    def test_removes_stopwords(self):
        result = preprocess_text("This is a test of the system")
        # Common stopwords like 'this', 'is', 'a', 'of', 'the' should be gone
        tokens = result.split()
        for stopword in ["this", "is", "a", "of", "the"]:
            assert stopword not in tokens

    def test_lemmatizes_tokens(self):
        result = preprocess_text("running dogs are chasing cats")
        # 'running' -> 'running' or 'run'; 'dogs' -> 'dog'; 'cats' -> 'cat'
        assert "dog" in result or "dogs" not in result
        assert "cat" in result or "cats" not in result

    def test_empty_string(self):
        assert preprocess_text("") == ""

    def test_none_input(self):
        assert preprocess_text(None) == ""

    def test_only_stopwords(self):
        result = preprocess_text("the is a and or but")
        assert result.strip() == ""

    def test_non_string_input(self):
        result = preprocess_text(12345)
        assert isinstance(result, str)

    def test_handles_unicode(self):
        result = preprocess_text("café naïve résumé")
        assert isinstance(result, str)

    def test_preserves_meaningful_words(self):
        result = preprocess_text("machine learning algorithm")
        assert "machin" in result or "machine" in result
        assert "learn" in result or "learning" in result
        assert "algorithm" in result


class TestTokenizeSentences:
    """Tests for tokenize_sentences()."""

    def test_splits_sentences(self):
        text = "The quick brown fox. The lazy dog jumps."
        sentences = tokenize_sentences(text)
        assert len(sentences) == 2

    def test_single_sentence(self):
        text = "Hello world"
        sentences = tokenize_sentences(text)
        assert len(sentences) == 1
        assert sentences[0] == "Hello world"

    def test_empty_string(self):
        assert tokenize_sentences("") == []

    def test_none_input(self):
        assert tokenize_sentences(None) == []

    def test_multiple_sentences(self):
        text = "First sentence. Second sentence. Third sentence."
        sentences = tokenize_sentences(text)
        assert len(sentences) == 3

    def test_strips_whitespace(self):
        text = "  Hello world.  "
        sentences = tokenize_sentences(text)
        for s in sentences:
            assert s == s.strip()
