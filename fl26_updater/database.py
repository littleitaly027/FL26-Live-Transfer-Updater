"""SQLite database for transfer history and state management."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import structlog

from fl26_updater.models import Transfer, TransferType, VerificationStatus

logger = structlog.get_logger(__name__)


class TransferDatabase:
    """Manages transfer history and state in SQLite."""

    def __init__(self, db_path: str) -> None:
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize database schema if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS transfers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT NOT NULL,
                    source_club TEXT NOT NULL,
                    destination_club TEXT NOT NULL,
                    transfer_type TEXT NOT NULL,
                    source_player_id TEXT,
                    fl26_player_id INTEGER,
                    fl26_source_team_id INTEGER,
                    fl26_destination_team_id INTEGER,
                    source_url TEXT,
                    source_timestamp TIMESTAMP,
                    detected_timestamp TIMESTAMP NOT NULL,
                    confidence REAL NOT NULL,
                    verification_status TEXT NOT NULL,
                    applied BOOLEAN DEFAULT 0,
                    applied_timestamp TIMESTAMP,
                    skipped BOOLEAN DEFAULT 0,
                    skip_reason TEXT,
                    notes TEXT,
                    UNIQUE(player_name, source_club, destination_club, transfer_type)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS player_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER NOT NULL,
                    player_name TEXT NOT NULL,
                    ovr INTEGER NOT NULL,
                    position TEXT NOT NULL,
                    nationality TEXT NOT NULL,
                    data_hash TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    UNIQUE(player_id, timestamp)
                )
                """
            )
            conn.commit()

    def add_transfer(self, transfer: Transfer) -> bool:
        """Add or update a transfer record.
        
        Args:
            transfer: Transfer object to store
            
        Returns:
            True if inserted/updated, False if duplicate
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO transfers (
                        player_name, source_club, destination_club, transfer_type,
                        source_player_id, fl26_player_id, fl26_source_team_id, fl26_destination_team_id,
                        source_url, source_timestamp, detected_timestamp, confidence, verification_status, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(player_name, source_club, destination_club, transfer_type) DO UPDATE SET
                        confidence = excluded.confidence,
                        verification_status = excluded.verification_status,
                        source_timestamp = excluded.source_timestamp,
                        detected_timestamp = excluded.detected_timestamp
                    """,
                    (
                        transfer.player_name,
                        transfer.source_club,
                        transfer.destination_club,
                        transfer.transfer_type.value,
                        transfer.source_player_id,
                        transfer.fl26_player_id,
                        transfer.fl26_source_team_id,
                        transfer.fl26_destination_team_id,
                        transfer.source_url,
                        transfer.source_timestamp,
                        transfer.detected_timestamp,
                        transfer.confidence,
                        transfer.verification_status.value,
                        transfer.notes,
                    ),
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error("Failed to add transfer", error=str(e), player=transfer.player_name)
            return False

    def get_pending_transfers(self) -> List[Transfer]:
        """Get all pending transfers.
        
        Returns:
            List of Transfer objects with pending verification status
        """
        transfers = []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT * FROM transfers WHERE verification_status = ? AND applied = 0
                ORDER BY detected_timestamp DESC
                """,
                (VerificationStatus.PENDING.value,),
            ).fetchall()
            for row in rows:
                transfers.append(self._row_to_transfer(row))
        return transfers

    def get_applied_transfers(self, limit: int = 100) -> List[Transfer]:
        """Get recently applied transfers.
        
        Args:
            limit: Maximum number of transfers to return
            
        Returns:
            List of applied Transfer objects
        """
        transfers = []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT * FROM transfers WHERE applied = 1
                ORDER BY applied_timestamp DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            for row in rows:
                transfers.append(self._row_to_transfer(row))
        return transfers

    def mark_applied(self, transfer: Transfer) -> bool:
        """Mark a transfer as successfully applied.
        
        Args:
            transfer: Transfer object to mark
            
        Returns:
            True if updated successfully
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE transfers SET applied = 1, applied_timestamp = ?, verification_status = ?
                    WHERE player_name = ? AND source_club = ? AND destination_club = ? AND transfer_type = ?
                    """,
                    (
                        datetime.utcnow(),
                        VerificationStatus.APPLIED.value,
                        transfer.player_name,
                        transfer.source_club,
                        transfer.destination_club,
                        transfer.transfer_type.value,
                    ),
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error("Failed to mark transfer as applied", error=str(e))
            return False

    def _row_to_transfer(self, row: sqlite3.Row) -> Transfer:
        """Convert database row to Transfer object."""
        return Transfer(
            player_name=row["player_name"],
            source_club=row["source_club"],
            destination_club=row["destination_club"],
            transfer_type=TransferType(row["transfer_type"]),
            source_player_id=row["source_player_id"],
            fl26_player_id=row["fl26_player_id"],
            fl26_source_team_id=row["fl26_source_team_id"],
            fl26_destination_team_id=row["fl26_destination_team_id"],
            source_url=row["source_url"],
            source_timestamp=row["source_timestamp"],
            detected_timestamp=row["detected_timestamp"],
            confidence=row["confidence"],
            verification_status=VerificationStatus(row["verification_status"]),
            notes=row["notes"] or "",
        )
