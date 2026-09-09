from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


class HistoryLog:
    def __init__(self, path: Path):
        self.path = path

    def add(self, event: str, **details: Any) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        record: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
            "event": event,
            **details,
        }
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")

    def recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        if not self.path.exists():
            return []
        records = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return records[-max(1, limit):][::-1]

