"""Tests for player name normalization."""

import pytest
from fl26_updater.matching.normalization import normalize_name, split_name, get_name_variations


class TestNormalization:
    """Test player name normalization."""

    def test_normalize_name_basic(self):
        """Test basic name normalization."""
        assert normalize_name("John Doe") == "john doe"
        assert normalize_name("JOHN DOE") == "john doe"

    def test_normalize_name_accents(self):
        """Test accent removal."""
        assert normalize_name("José") == "jose"
        assert normalize_name("Müller") == "muller"
        assert normalize_name("Søren") == "soren"

    def test_normalize_name_punctuation(self):
        """Test punctuation removal."""
        assert normalize_name("O'Brien") == "obrien"
        assert normalize_name("Jean-Claude") == "jeanclaudة"

    def test_normalize_name_whitespace(self):
        """Test whitespace normalization."""
        assert normalize_name("John  Doe") == "john doe"
        assert normalize_name("  John Doe  ") == "john doe"

    def test_split_name_full(self):
        """Test full name splitting."""
        first, last = split_name("John Michael Doe")
        assert first == "John"
        assert last == "Doe"

    def test_split_name_partial(self):
        """Test single name."""
        first, last = split_name("Ronaldo")
        assert first == "Ronaldo"
        assert last == ""

    def test_get_name_variations(self):
        """Test name variation generation."""
        variations = get_name_variations("John Doe")
        assert "John Doe" in variations
        assert "john doe" in variations
        assert "Doe" in variations or "doe" in variations


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
