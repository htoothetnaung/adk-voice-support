"""JSON trace logging for conversations and evaluation runs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from app.services.response_parser import SupportResponse


class TraceLogger:
    """Persist structured traces under `logs/`."""

    def __init__(self, log_dir: str | Path = "logs") -> None:
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def save_turn(self, response: SupportResponse, prefix: str = "conversation") -> Path:
        """Save one runner response as a timestamped JSON file."""

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        path = self.log_dir / f"{prefix}_{timestamp}.json"
        payload = response.to_dict()
        payload["logged_at"] = datetime.now(timezone.utc).isoformat()
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

