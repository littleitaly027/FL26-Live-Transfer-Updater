"""Player matching confidence scoring."""

from difflib import SequenceMatcher
from typing import Optional
import structlog

from fl26_updater.matching.normalization import normalize_name, get_name_variations
from fl26_updater.models import MatchResult

logger = structlog.get_logger(__name__)


class PlayerMatcher:
    """Matches players from external sources to FL26 database."""

    def __init__(self, min_confidence: float = 0.7) -> None:
        """Initialize player matcher.
        
        Args:
            min_confidence: Minimum confidence threshold for matches (0-1)
        """
        self.min_confidence = min_confidence

    def match_player(
        self,
        source_name: str,
        fl26_candidates: dict[int, str],
    ) -> MatchResult:
        """Match a source player to FL26 database.
        
        Args:
            source_name: Player name from external source
            fl26_candidates: Dictionary of {player_id: player_name} from FL26
            
        Returns:
            MatchResult with best match and confidence
        """
        if not fl26_candidates:
            return MatchResult(source_player_name=source_name, confidence=0.0)

        best_match_id: Optional[int] = None
        best_match_name: Optional[str] = None
        best_confidence = 0.0
        alternatives = []

        # Generate variations of source name for matching
        source_variations = get_name_variations(source_name)
        source_normalized = normalize_name(source_name)

        for player_id, fl26_name in fl26_candidates.items():
            fl26_normalized = normalize_name(fl26_name)
            
            # Check exact normalized match
            if source_normalized == fl26_normalized:
                confidence = 1.0
                match_type = "exact"
            else:
                # Calculate similarity
                confidence = self._calculate_similarity(
                    source_normalized, fl26_normalized, source_variations
                )
                match_type = "fuzzy" if confidence > 0.8 else "alias"

            if confidence >= best_confidence:
                if confidence > best_confidence:
                    # Found new best match
                    if best_match_id is not None:
                        alternatives.append((best_match_id, best_match_name or "", best_confidence))
                    best_match_id = player_id
                    best_match_name = fl26_name
                    best_confidence = confidence
                elif confidence == best_confidence and confidence > 0.85:
                    # Equal confidence match - ambiguous
                    alternatives.append((player_id, fl26_name, confidence))

        return MatchResult(
            source_player_name=source_name,
            fl26_player_id=best_match_id,
            fl26_player_name=best_match_name,
            confidence=best_confidence,
            match_type="exact" if best_confidence >= 0.95 else "normalized",
            is_ambiguous=len(alternatives) > 0 and best_confidence == alternatives[0][2],
            alternatives=alternatives,
        )

    def _calculate_similarity(self, norm_source: str, norm_fl26: str, source_variations: list[str]) -> float:
        """Calculate similarity score between normalized names.
        
        Args:
            norm_source: Normalized source name
            norm_fl26: Normalized FL26 name
            source_variations: List of name variations
            
        Returns:
            Similarity score (0-1)
        """
        # Direct comparison
        ratio = SequenceMatcher(None, norm_source, norm_fl26).ratio()
        
        # Check if any variation matches
        for variation in source_variations:
            variation_norm = normalize_name(variation)
            if variation_norm == norm_fl26:
                return 0.95
            variation_ratio = SequenceMatcher(None, variation_norm, norm_fl26).ratio()
            if variation_ratio > ratio:
                ratio = variation_ratio
        
        return ratio
