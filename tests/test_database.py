"""Tests for transfer database."""

import pytest
import tempfile
from pathlib import Path

from fl26_updater.database import TransferDatabase
from fl26_updater.models import Transfer, TransferType, VerificationStatus


class TestTransferDatabase:
    """Test transfer database operations."""

    def setup_method(self):
        """Set up test database."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.temp_db.name
        self.db = TransferDatabase(self.db_path)

    def teardown_method(self):
        """Clean up test database."""
        Path(self.db_path).unlink(missing_ok=True)

    def test_add_transfer(self):
        """Test adding a transfer."""
        transfer = Transfer(
            player_name="John Doe",
            source_club="Manchester United",
            destination_club="Liverpool",
            transfer_type=TransferType.PERMANENT,
            confidence=0.95,
        )
        result = self.db.add_transfer(transfer)
        assert result is True

    def test_get_pending_transfers(self):
        """Test retrieving pending transfers."""
        transfer = Transfer(
            player_name="John Doe",
            source_club="Manchester United",
            destination_club="Liverpool",
            transfer_type=TransferType.PERMANENT,
            confidence=0.95,
            verification_status=VerificationStatus.PENDING,
        )
        self.db.add_transfer(transfer)
        
        pending = self.db.get_pending_transfers()
        assert len(pending) == 1
        assert pending[0].player_name == "John Doe"

    def test_mark_applied(self):
        """Test marking transfer as applied."""
        transfer = Transfer(
            player_name="John Doe",
            source_club="Manchester United",
            destination_club="Liverpool",
            transfer_type=TransferType.PERMANENT,
            confidence=0.95,
        )
        self.db.add_transfer(transfer)
        result = self.db.mark_applied(transfer)
        assert result is True
        
        applied = self.db.get_applied_transfers()
        assert len(applied) == 1
        assert applied[0].verification_status == VerificationStatus.APPLIED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
