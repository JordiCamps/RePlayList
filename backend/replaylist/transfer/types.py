"""Types and results for playlist transfers."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class TransferStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TransferProgress:
    transfer_id: str
    status: TransferStatus
    completed: int = 0
    total: int = 0
    current_track: str = ""
    error_message: str = ""
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


@dataclass
class TransferResult:
    transfer_id: str
    status: TransferStatus
    source_playlist: Dict[str, Any]
    target_playlist: Dict[str, Any]
    success_count: int = 0
    fail_count: int = 0
    failed_tracks: List[Dict[str, Any]] = field(default_factory=list)
    skipped_tracks: List[Dict[str, Any]] = field(default_factory=list)
    created_playlist: Optional[Dict[str, Any]] = None
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


