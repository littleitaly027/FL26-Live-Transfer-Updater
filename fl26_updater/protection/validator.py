"""Validates and protects player data during transfers."""

import hashlib
from datetime import datetime
from typing import Optional, Set
import structlog

from fl26_updater.models import PlayerSnapshot, Transfer

logger = structlog.get_logger(__name__)


class DataProtector:
    """Protects player attribute data against accidental modification."""

    def __init__(self) -> None:
        """Initialize data protector."""
        self.snapshots: dict[int, PlayerSnapshot] = {}

    def create_snapshot(self, player_id: int, player_name: str, ovr: int, position: str, nationality: str) -> PlayerSnapshot:
        """Create a snapshot of player data before transfer.
        
        Args:
            player_id: FL26 player ID
            player_name: Player name
            ovr: Overall rating
            position: Player position
            nationality: Player nationality
            
        Returns:
            PlayerSnapshot object
        """
        data_hash = self._hash_player_data(player_id, player_name, ovr, position, nationality)
        snapshot = PlayerSnapshot(
            player_id=player_id,
            player_name=player_name,
            ovr=ovr,
            position=position,
            nationality=nationality,
            data_hash=data_hash,
            timestamp=datetime.utcnow(),
        )
        self.snapshots[player_id] = snapshot
        logger.info("snapshot_created", player_id=player_id, hash=data_hash)
        return snapshot

    def validate_snapshot(self, player_id: int, player_name: str, ovr: int, position: str, nationality: str) -> bool:
        """Validate that protected fields haven't changed.
        
        Args:
            player_id: FL26 player ID
            player_name: Current player name
            ovr: Current overall rating
            position: Current position
            nationality: Current nationality
            
        Returns:
            True if data matches snapshot, False if changed
        """
        if player_id not in self.snapshots:
            return True  # No snapshot, so can't validate
        
        snapshot = self.snapshots[player_id]
        
        # Check critical fields
        protected_fields = {
            "name": (player_name, snapshot.player_name),
            "ovr": (ovr, snapshot.ovr),
            "position": (position, snapshot.position),
            "nationality": (nationality, snapshot.nationality),
        }
        
        changed_fields = []
        for field, (current, original) in protected_fields.items():
            if current != original:
                changed_fields.append(field)
        
        if changed_fields:
            logger.warning(
                "protected_fields_changed",
                player_id=player_id,
                changed=changed_fields,
            )
            return False
        
        return True

    def get_protected_fields(self, player_id: int) -> Optional[dict]:
        """Get the protected field values for a player.
        
        Args:
            player_id: FL26 player ID
            
        Returns:
            Dictionary of protected fields or None if no snapshot
        """
        if player_id not in self.snapshots:
            return None
        
        snapshot = self.snapshots[player_id]
        return {
            "player_name": snapshot.player_name,
            "ovr": snapshot.ovr,
            "position": snapshot.position,
            "nationality": snapshot.nationality,
        }

    def _hash_player_data(self, player_id: int, name: str, ovr: int, position: str, nationality: str) -> str:
        """Create hash of player data for integrity checking.
        
        Args:
            player_id: Player ID
            name: Player name
            ovr: Overall rating
            position: Position
            nationality: Nationality
            
        Returns:
            SHA256 hash
        """
        data = f"{player_id}:{name}:{ovr}:{position}:{nationality}"
        return hashlib.sha256(data.encode()).hexdigest()
