"""PES 2021 / Football Life 26 EDIT file binary format structure and constants.

This module documents the discovered structure of the EDIT00000000 file format
based on community research and reverse engineering.

WARNING: The EDIT format is not officially documented by Konami/Konami Digital.
This implementation is based on community findings and should be thoroughly tested
before production use.

STRUCTURE OVERVIEW:
- The EDIT00000000 file is a binary container for game edits and custom data
- It contains multiple data sections: players, teams, kits, managers, etc.
- Player records are fixed-length (0xCC / 204 bytes each)
- Team squad assignments are stored in a separate section
- File structure can vary slightly between game versions and DLC updates

CRITICAL RULES FOR SAFE MODIFICATION:
1. NEVER modify player stats, attributes, appearance, age, position, skills
2. ONLY modify player club/team assignment fields
3. ALWAYS create backup before writing
4. ALWAYS validate file integrity after modification
5. Preserve all unknown/undocumented bytes exactly as-is
6. Restore from backup if validation fails
"""

import struct
from enum import IntEnum
from dataclasses import dataclass
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class EditFileVersion(IntEnum):
    """Supported EDIT file versions."""
    PES_2021 = 2021
    FL26_V1 = 260  # Football Life 26 variant 1


class PlayerPosition(IntEnum):
    """Player registered positions in PES 2021."""
    GK = 0x00  # Goalkeeper
    CB = 0x01  # Center Back
    LB = 0x02  # Left Back
    RB = 0x03  # Right Back
    DMF = 0x04  # Defensive Midfielder
    CMF = 0x05  # Central Midfielder
    LMF = 0x06  # Left Midfielder
    RMF = 0x07  # Right Midfielder
    AMF = 0x08  # Attacking Midfielder
    LWF = 0x09  # Left Wing Forward
    RWF = 0x0A  # Right Wing Forward
    CF = 0x0B  # Center Forward
    ST = 0x0C  # Striker


# ============================================================================
# FILE-LEVEL CONSTANTS
# ============================================================================

# Typical offsets (can vary by version/DLC)
DEFAULT_PLAYER_SECTION_OFFSET = 0x2D090  # Approximate offset where player data begins
DEFAULT_TEAM_SECTION_OFFSET = 0x120000  # Approximate offset where team squad data begins

# Player record size
PLAYER_RECORD_SIZE = 0xCC  # 204 bytes per player record

# Number of player slots (including unused/dummy)
MAX_PLAYERS = 25000  # Approximate

# ============================================================================
# PLAYER RECORD FIELD OFFSETS (within each 0xCC record)
# ============================================================================

class PlayerRecordOffsets:
    """Field offsets within a single player record (204 bytes / 0xCC)."""
    
    PLAYER_ID = 0x00  # 4 bytes - Little Endian uint32
    NATIONALITY = 0x04  # 2 bytes - uint16 country code
    UNKNOWN_06 = 0x06  # 2 bytes - typically unused
    FACE_INDEX = 0x08  # 2 bytes - appearance face file index
    HAIR_INDEX = 0x0A  # 2 bytes - appearance hair file index
    HEIGHT = 0x0C  # 1 byte - player height in cm (150-205+)
    WEIGHT = 0x0D  # 1 byte - player weight in kg (50-110+)
    AGE = 0x0E  # 1 byte - player age (15-45)
    STRONGER_FOOT = 0x0F  # 1 byte - 0=Right, 1=Left
    REGISTERED_POSITION = 0x10  # 1 byte - main position
    
    # PROTECTED STATS - DO NOT MODIFY
    # Offsets 0x11-0x1F contain player abilities/stats (Attack, Defense, etc.)
    # Offsets 0x20-0x3F contain skill/special ability data
    # These are CRITICAL and must never be changed during transfer
    
    # CLUB/TEAM ASSIGNMENT (the ONLY field we should modify)
    # Offset 0x50-0x51: Current team/club ID (Little Endian uint16)
    # This is what changes during a transfer
    CURRENT_CLUB_ID = 0x50  # 2 bytes - Little Endian uint16
    
    # Additional fields follow but should not be modified
    # Offsets 0x52+ contain kits, accessories, squad position, etc.


class PlayerRecord:
    """Represents a single player record from EDIT file."""
    
    def __init__(self, data: bytes, offset: int = 0):
        """Initialize player record from binary data.
        
        Args:
            data: Raw bytes of the player record (must be at least 0xCC bytes)
            offset: Starting offset in the data (default 0)
        """
        if len(data) - offset < PLAYER_RECORD_SIZE:
            raise ValueError(
                f"Insufficient data for player record: "
                f"need {PLAYER_RECORD_SIZE}, got {len(data) - offset}"
            )
        
        self.raw_data = bytearray(data[offset:offset + PLAYER_RECORD_SIZE])
        self._parse_fields()
    
    def _parse_fields(self) -> None:
        """Parse individual fields from raw data."""
        # Read player ID (Little Endian)
        self.player_id = struct.unpack_from(
            "<I", self.raw_data, PlayerRecordOffsets.PLAYER_ID
        )[0]
        
        # Read nationality
        self.nationality = struct.unpack_from(
            "<H", self.raw_data, PlayerRecordOffsets.NATIONALITY
        )[0]
        
        # Read appearance indices
        self.face_index = struct.unpack_from(
            "<H", self.raw_data, PlayerRecordOffsets.FACE_INDEX
        )[0]
        
        self.hair_index = struct.unpack_from(
            "<H", self.raw_data, PlayerRecordOffsets.HAIR_INDEX
        )[0]
        
        # Read physical attributes (PROTECTED - must not change)
        self.height = self.raw_data[PlayerRecordOffsets.HEIGHT]
        self.weight = self.raw_data[PlayerRecordOffsets.WEIGHT]
        self.age = self.raw_data[PlayerRecordOffsets.AGE]
        
        # Read foot and position
        self.stronger_foot = self.raw_data[PlayerRecordOffsets.STRONGER_FOOT]
        self.registered_position = self.raw_data[PlayerRecordOffsets.REGISTERED_POSITION]
        
        # Read current club (THIS IS WHAT WE CAN MODIFY)
        self.current_club_id = struct.unpack_from(
            "<H", self.raw_data, PlayerRecordOffsets.CURRENT_CLUB_ID
        )[0]
    
    def get_club_id(self) -> int:
        """Get current club ID for this player."""
        return self.current_club_id
    
    def set_club_id(self, new_club_id: int) -> bool:
        """Safely set player's club ID for transfer.
        
        Args:
            new_club_id: New club ID (0-65535)
            
        Returns:
            True if successful, False if invalid
        """
        if not isinstance(new_club_id, int) or new_club_id < 0 or new_club_id > 0xFFFF:
            logger.error(f"Invalid club ID: {new_club_id}")
            return False
        
        # Update the in-memory value
        self.current_club_id = new_club_id
        
        # Update the raw bytes (Little Endian)
        struct.pack_into(
            "<H", self.raw_data, PlayerRecordOffsets.CURRENT_CLUB_ID, new_club_id
        )
        
        logger.info(f"Player {self.player_id} club changed to {new_club_id}")
        return True
    
    def get_raw_bytes(self) -> bytes:
        """Get the complete player record as bytes."""
        return bytes(self.raw_data)
    
    def create_snapshot(self) -> dict:
        """Create a snapshot of protected fields for validation."""
        return {
            "player_id": self.player_id,
            "height": self.height,
            "weight": self.weight,
            "age": self.age,
            "registered_position": self.registered_position,
            "face_index": self.face_index,
            "hair_index": self.hair_index,
            "nationality": self.nationality,
        }
    
    def validate_against_snapshot(self, snapshot: dict) -> bool:
        """Validate that protected fields match a snapshot.
        
        Args:
            snapshot: Previously saved snapshot
            
        Returns:
            True if all protected fields match
        """
        checks = [
            ("player_id", self.player_id, snapshot.get("player_id")),
            ("height", self.height, snapshot.get("height")),
            ("weight", self.weight, snapshot.get("weight")),
            ("age", self.age, snapshot.get("age")),
            ("registered_position", self.registered_position, snapshot.get("registered_position")),
            ("face_index", self.face_index, snapshot.get("face_index")),
            ("hair_index", self.hair_index, snapshot.get("hair_index")),
            ("nationality", self.nationality, snapshot.get("nationality")),
        ]
        
        all_valid = True
        for field_name, current, expected in checks:
            if current != expected:
                logger.warning(
                    f"Protected field mismatch for player {self.player_id}: "
                    f"{field_name} changed from {expected} to {current}"
                )
                all_valid = False
        
        return all_valid


@dataclass
class EditFileMetadata:
    """Metadata about an EDIT file."""
    file_path: str
    file_size: int
    version: EditFileVersion
    player_section_offset: int
    team_section_offset: int
    player_count: int
    header_bytes: Optional[bytes] = None  # First N bytes (header)
