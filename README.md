# 2D縦スクロール・ジャンピングゲーム（pyxel）

隣接リポジトリ `../2d_game`（pygame版）の仕様・内容を、pyxelで再構築した版です。

## セットアップ

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m game
```

## 操作

- ← / →: 移動
- Space（または Z）: ジャンプ（長押しで貯め、離して発射）
- Enter: 決定
- Esc: 戻る（タイトルでEscは終了）

## 保存

- `save/highscore.json`: ハイスコア
- `save/runs.json`: 直近のプレイ結果（ランキング表示用）

## キャラクタ生成（ローディング）

番人の入力後、ローディングバー表示中にキャラクタを生成します（デフォルトはローカルの決定論的生成）。

- 外部コマンドで生成したい場合は `GAME_CHARACTER_GENERATE_CMD` を設定します。
  - `{prompt}` と `{out}` が置換されます（`{out}` は `save/generated_character.json` を想定）。

## フォント（日本語表示）

pyxelの標準フォントは日本語に対応しないため、この実装では Pillow でTTF/OTFからラスタライズして表示します。

- `GAME_FONT_PATH`（単一）または `GAME_FONT_PATHS`（複数）を設定できます（複数は `:` 区切り、Windowsは `;` 区切り）。

