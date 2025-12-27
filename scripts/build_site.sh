#!/usr/bin/env bash
set -euo pipefail

rm -rf site
mkdir -p site

# Startup for <pyxel-run>
cat > site/main.py <<'PY'
from game.app import run

if __name__ == "__main__":
    run()
PY

# Copy sources and shared config
cp -f config.toml site/config.toml
cp -rf game site/game

# Pyxel WASM loader may use synchronous XHR against directory paths.
# GitHub Pages serves directories only when an index.html exists, so add minimal ones.
for d in \
  site/game \
  site/game/scenes \
  site/game/entities
do
  mkdir -p "$d"
  printf '%s\n' '<!doctype html><meta charset="utf-8"><title>dir</title>' > "$d/index.html"
done

cat > site/index.html <<'HTML'
<!doctype html>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>2d_game_pyxel</title>
<script src="https://cdn.jsdelivr.net/gh/kitao/pyxel@2.5.11/wasm/pyxel.js"></script>
<style>
html, body { margin: 0; padding: 0; overflow: hidden; background: #000; }
canvas { outline: none; }
</style>
<script>
// Prevent arrow keys from scrolling the page while playing.
window.addEventListener("keydown", (e) => {
  const keys = ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", " "];
  if (keys.includes(e.key)) e.preventDefault();
}, { passive: false });

// iOS Safari blocks audio until a user gesture.
// On tap/click, resume the underlying SDL2 AudioContext if needed.
function tryResumePyxelAudio() {
  const audioContext = window.pyxelContext?.pyodide?._module?.SDL2?.audioContext;
  if (!audioContext) return;
  if (audioContext.state === "running") return;
  audioContext.resume?.().catch?.(() => {});
}
document.addEventListener("touchstart", tryResumePyxelAudio, { passive: true });
document.addEventListener("click", tryResumePyxelAudio, { passive: true });

// Ensure the Pyxel canvas can receive keyboard focus.
function focusPyxelCanvas() {
  const c = document.querySelector("canvas");
  if (!c) return false;
  c.tabIndex = 0;
  c.focus();
  c.addEventListener("pointerdown", () => c.focus());
  return true;
}

let tries = 0;
const t = setInterval(() => {
  tries += 1;
  if (focusPyxelCanvas() || tries > 300) clearInterval(t);
}, 50);
</script>

<pyxel-run root="." name="main.py" gamepad="enabled"></pyxel-run>
HTML

printf '%s\n' "" > site/.nojekyll
echo "Built: site/index.html"

