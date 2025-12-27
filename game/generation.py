from __future__ import annotations

import json
import os
import shlex
import subprocess
import threading
import time
from dataclasses import dataclass

from game.character import CharacterSpec


def _read_json(path: str) -> dict | None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


@dataclass
class GenerationResult:
    ok: bool
    spec: CharacterSpec
    debug: str


class GenerationJob:
    def __init__(self, prompt: str, seed: int) -> None:
        self.prompt = prompt
        self.seed = seed
        self.progress: float = 0.0
        self.done: bool = False
        self.result: GenerationResult | None = None
        self._lock = threading.Lock()
        self._start = time.time()
        self._cooperative: bool = False

    def start(self) -> None:
        try:
            t = threading.Thread(target=self._run, daemon=True)
            t.start()
        except RuntimeError:
            # Some runtimes (e.g., Pyodide/Web) can't start threads.
            # Fall back to cooperative (single-thread) progress driven by snapshot().
            with self._lock:
                self._cooperative = True
                self._start = time.time()

    def _set_progress(self, value: float) -> None:
        with self._lock:
            self.progress = max(self.progress, min(1.0, value))

    def _finish(self, result: GenerationResult) -> None:
        with self._lock:
            self.progress = 1.0
            self.done = True
            self.result = result

    def snapshot(self) -> tuple[float, bool, GenerationResult | None]:
        with self._lock:
            cooperative = self._cooperative and (not self.done)
        if cooperative:
            # Drive pseudo-progress without sleeping.
            elapsed = time.time() - self._start
            self._set_progress(min(0.95, elapsed / 1.2))
            if elapsed >= 1.2 and not self.done:
                spec = CharacterSpec.from_seed(self.seed)
                self._finish(GenerationResult(ok=True, spec=spec, debug="cooperative deterministic"))
        with self._lock:
            return self.progress, self.done, self.result

    def _run(self) -> None:
        def tick() -> None:
            elapsed = time.time() - self._start
            self._set_progress(min(0.90, elapsed / 1.8))

        try:
            cmd_tpl = os.environ.get("GAME_CHARACTER_GENERATE_CMD")
            out_path = os.path.join("save", "generated_character.json")
            os.makedirs(os.path.dirname(out_path), exist_ok=True)

            if cmd_tpl:
                tick()
                cmd_str = cmd_tpl.format(prompt=self.prompt, out=out_path)
                args = shlex.split(cmd_str)
                proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                while proc.poll() is None:
                    tick()
                    time.sleep(0.05)
                tick()
                stdout, stderr = proc.communicate(timeout=0.2)
                data = _read_json(out_path)
                if proc.returncode == 0 and isinstance(data, dict):
                    spec = CharacterSpec.from_dict(data)
                    self._finish(GenerationResult(ok=True, spec=spec, debug=f"external ok: {cmd_str}"))
                else:
                    spec = CharacterSpec.from_seed(self.seed)
                    self._finish(
                        GenerationResult(
                            ok=False,
                            spec=spec,
                            debug=f"external failed rc={proc.returncode} stdout={stdout[:120]} stderr={stderr[:120]}",
                        )
                    )
                return

            for _ in range(18):
                tick()
                time.sleep(0.03)

            spec = CharacterSpec.from_seed(self.seed)
            self._finish(GenerationResult(ok=True, spec=spec, debug="local deterministic"))
        except Exception as e:
            spec = CharacterSpec.from_seed(self.seed)
            self._finish(GenerationResult(ok=False, spec=spec, debug=f"exception: {type(e).__name__}"))
