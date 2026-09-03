"""Tests for player matching."""

import pytest
from fl26_updater.matching.scorer import PlayerMatcher


class TestPlayerMatcher:
    """Test player matching functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.matcher = PlayerMatcher(min_confidence=0.7)

    def test_exact_match(self):
        """Test exact player name match."""
        fl26_candidates = {
            1: "John Doe",
            2: "Jane Smith",
        }
        result = self.matcher.match_player("John Doe", fl26_candidates)
        assert result.fl26_player_id == 1
        assert result.confidence >= 0.95

    def test_normalized_match(self):
        """Test normalized name match."""
        fl26_candidates = {
            1: "John Doe",
            2: "Jane Smith",
        }
        result = self.matcher.match_player("JOHN DOE", fl26_candidates)
        assert result.fl26_player_id == 1
        assert result.confidence >= 0.95

    def test_fuzzy_match(self):
        """Test fuzzy name matching."""
        fl26_candidates = {
            1: "John Doe",
            2: "Jane Smith",
        }
        result = self.matcher.match_player("Jon Doe", fl26_candidates)
        # Should still match with high confidence
        assert result.fl26_player_id == 1
        assert result.confidence > 0.7

    def test_no_match(self):
        """Test when no suitable match exists."""
        fl26_candidates = {
            1: "John Doe",
            2: "Jane Smith",
        }
        result = self.matcher.match_player("Completely Different", fl26_candidates)
        assert result.confidence < 0.7

    def test_empty_candidates(self):
        """Test with empty candidate list."""
        result = self.matcher.match_player("John Doe", {})
        assert result.fl26_player_id is None
        assert result.confidence == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
