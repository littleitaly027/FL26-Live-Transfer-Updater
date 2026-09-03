"""Data models for transfer management and player matching."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List


class TransferType(str, Enum):
    """Types of football transfers."""

    PERMANENT = "permanent"
    LOAN = "loan"
    LOAN_RETURN = "loan_return"
    FREE_TRANSFER = "free_transfer"
    RELEASE = "release"
    PROMOTION = "promotion"
    RELEGATION = "relegation"
    UNKNOWN = "unknown"


class VerificationStatus(str, Enum):
    """Verification status of a transfer."""

    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    APPLIED = "applied"
    FAILED = "failed"


@dataclass
class Transfer:
    """Represents a real-world football transfer."""

    player_name: str
    source_club: str
    destination_club: str
    transfer_type: TransferType = TransferType.PERMANENT
    source_player_id: Optional[str] = None
    source_url: Optional[str] = None
    source_timestamp: Optional[datetime] = None
    detected_timestamp: datetime = field(default_factory=datetime.utcnow)
    confidence: float = 0.0
    verification_status: VerificationStatus = VerificationStatus.PENDING
    fl26_player_id: Optional[int] = None
    fl26_source_team_id: Optional[int] = None
    fl26_destination_team_id: Optional[int] = None
    notes: str = ""

    def __hash__(self) -> int:
        """Make Transfer hashable using unique identifiers."""
        return hash((self.player_name, self.source_club, self.destination_club, self.transfer_type))


@dataclass
class MatchResult:
    """Result of player matching between external source and FL26 database."""

    source_player_name: str
    fl26_player_id: Optional[int] = None
    fl26_player_name: Optional[str] = None
    confidence: float = 0.0
    match_type: str = "unknown"  # exact, normalized, alias, etc.
    secondary_evidence: List[str] = field(default_factory=list)
    is_ambiguous: bool = False
    alternatives: List[tuple[int, str, float]] = field(default_factory=list)  # (player_id, name, confidence)


@dataclass
class PlayerSnapshot:
    """Snapshot of protected player data for validation."""

    player_id: int
    player_name: str
    ovr: int
    position: str
    nationality: str
    data_hash: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class UpdateReport:
    """Summary report of an update operation."""

    scan_timestamp: datetime
    transfers_detected: int = 0
    transfers_applied: int = 0
    transfers_pending_review: int = 0
    transfers_skipped: int = 0
    failed_operations: int = 0
    validation_passed: bool = False
    protected_data_preserved: bool = False
    output_edit_version: str = ""
    error_messages: List[str] = field(default_factory=list)
