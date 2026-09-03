"""Player name normalization for matching."""

import unicodedata
import re
from typing import List


def normalize_name(name: str) -> str:
    """Normalize a player name for comparison.
    
    Handles:
    - Lowercase conversion
    - Punctuation removal
    - Accent removal
    - Extra whitespace
    
    Args:
        name: Original player name
        
    Returns:
        Normalized name
    """
    if not name:
        return ""
    
    # Remove accents
    nfd = unicodedata.normalize("NFD", name)
    name = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    
    # Lowercase
    name = name.lower()
    
    # Remove punctuation except spaces
    name = re.sub(r"[^a-z0-9\s]", "", name)
    
    # Normalize whitespace
    name = re.sub(r"\s+", " ", name).strip()
    
    return name


def split_name(name: str) -> tuple[str, str]:
    """Split a full name into first and last name.
    
    Args:
        name: Full name
        
    Returns:
        Tuple of (first_name, last_name)
    """
    parts = name.strip().split()
    if len(parts) <= 1:
        return name, ""
    return parts[0], parts[-1]


def get_name_variations(name: str) -> List[str]:
    """Generate common name variations.
    
    Args:
        name: Original name
        
    Returns:
        List of name variations
    """
    variations = [name]
    normalized = normalize_name(name)
    if normalized not in variations:
        variations.append(normalized)
    
    first, last = split_name(name)
    if last and f"{last} {first}" not in variations:
        variations.append(f"{last} {first}")
    
    if last:
        variations.append(last)
        variations.append(first)
    
    return [v for v in variations if v]  # Remove empty strings
