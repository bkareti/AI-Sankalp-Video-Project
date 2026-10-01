"""QA report data: per-check results, overall status, JSON and text output."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List

PASS = "pass"
NEEDS_REVIEW = "needs_review"
FAIL = "fail"
SEVERITY = {PASS: 0, NEEDS_REVIEW: 1, FAIL: 2}
REPORT_VERSION = 1


@dataclass
class CheckResult:
    id: str
    title: str
    status: str
    message: str
    fix: str = ""
    details: List[str] = field(default_factory=list)


@dataclass
class QAReport:
    slug: str
    created_at: str
    inputs: Dict[str, Any]
    checks: List[CheckResult]

    @property
    def status(self) -> str:
        return max((check.status for check in self.checks), key=SEVERITY.__getitem__, default=PASS)

    @property
    def final_ready(self) -> bool:
        return bool(self.checks) and all(check.status == PASS for check in self.checks)

    @property
    def summary(self) -> str:
        failed = sum(check.status == FAIL for check in self.checks)
        review = sum(check.status == NEEDS_REVIEW for check in self.checks)
        if self.final_ready:
            return f"All {len(self.checks)} checks passed. Final-ready."
        parts = []
        if failed:
            parts.append(f"{failed} check{'s' if failed != 1 else ''} failed")
        if review:
            parts.append(f"{review} need{'s' if review == 1 else ''} review")
        return ", ".join(parts).capitalize() + ". Not final-ready."

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_version": REPORT_VERSION,
            "slug": self.slug,
            "created_at": self.created_at,
            "status": self.status,
            "final_ready": self.final_ready,
            "summary": self.summary,
            "inputs": self.inputs,
            "checks": [asdict(check) for check in self.checks],
        }

    def format_text(self) -> str:
        labels = {PASS: "PASS", NEEDS_REVIEW: "REVIEW", FAIL: "FAIL"}
        lines = [f"QA report for {self.slug}: {labels[self.status]}", f"  {self.summary}", ""]
        for check in self.checks:
            lines.append(f"  [{labels[check.status]:6}] {check.title}")
            if check.status != PASS:
                lines.append(f"           Why: {check.message}")
                for detail in check.details[:8]:
                    lines.append(f"             - {detail}")
                if len(check.details) > 8:
                    lines.append(f"             ... and {len(check.details) - 8} more (see the JSON report)")
                if check.fix:
                    lines.append(f"           Fix: {check.fix}")
        return "\n".join(lines)


def write_report(report: QAReport, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
