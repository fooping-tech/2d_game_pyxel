from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _read_json(path: str, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _write_json_atomic(path: str, data) -> None:
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)


@dataclass(frozen=True)
class RunRecord:
    floor: int
    reason: str
    prompt: str
    ts: str

    @classmethod
    def create(cls, *, floor: int, reason: str, prompt: str) -> "RunRecord":
        return cls(floor=floor, reason=reason, prompt=prompt, ts=_utc_now_iso())


class ScoreStore:
    def __init__(self, save_dir: str = "save") -> None:
        self.save_dir = save_dir
        self.highscore_path = os.path.join(save_dir, "highscore.json")
        self.runs_path = os.path.join(save_dir, "runs.json")

        self.highscore: int = 0
        self.runs: list[RunRecord] = []

    def load(self) -> None:
        _ensure_dir(self.save_dir)
        hs = _read_json(self.highscore_path, {"highscore": 0})
        try:
            self.highscore = int(hs.get("highscore", 0))
        except Exception:
            self.highscore = 0

        raw_runs = _read_json(self.runs_path, [])
        runs: list[RunRecord] = []
        if isinstance(raw_runs, list):
            for r in raw_runs:
                try:
                    runs.append(
                        RunRecord(
                            floor=int(r.get("floor", 0)),
                            reason=str(r.get("reason", "")),
                            prompt=str(r.get("prompt", "")),
                            ts=str(r.get("ts", "")),
                        )
                    )
                except Exception:
                    continue
        self.runs = runs

    def record(self, rec: RunRecord) -> None:
        _ensure_dir(self.save_dir)
        self.runs.append(rec)
        self.runs = self.runs[-100:]
        if rec.floor > self.highscore:
            self.highscore = rec.floor
        self.save()

    def save(self) -> None:
        try:
            _write_json_atomic(self.highscore_path, {"highscore": self.highscore})
            _write_json_atomic(self.runs_path, [asdict(r) for r in self.runs])
        except Exception:
            return

    def top(self, n: int = 10) -> list[RunRecord]:
        return sorted(self.runs, key=lambda r: (r.floor, r.ts), reverse=True)[:n]

