# 2D縦スクロール・ジャンピングゲーム（pyxel）

隣接リポジトリ `../2d_game`（pygame版）の仕様・内容を、pyxelで再構築した版です。

## セットアップ

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m game
```

## 設定（.env）

調整用の設定は `.env` に書けます（起動時に読み込みます）。

- `GAME_SCROLL_START_PLAYER_SCREEN_Y`
- `GAME_FALL_BELOW_SCREEN_PX`
- `GAME_WATER_START_OFFSET`
- `GAME_WATER_BASE_SPEED`
- `GAME_WATER_SPEED_PER_FLOOR`
- `GAME_ZONE_FLOOR_STEP`
- `GAME_ZONE_POPUP_SECONDS`
- `GAME_ZONE_TEXT_FONT_PX`
- `GAME_ZONE_TEXT_FONT_PX_BIG`
- `GAME_SFX_VOLUME`
- `GAME_BGM_VOLUME`
- `GAME_TITLE_FONT_PX_BIG`
- `GAME_GAME_OVER_FONT_PX_BIG`

## GitHub Pages（HTML版の公開）

GitHub ActionsでHTML版をビルドしてGitHub Pagesへデプロイできます。

### セットアップ（初回のみ）

- GitHubのリポジトリ設定 `Settings → Pages` を開き、`Build and deployment` の `Source` を `GitHub Actions` に設定します。
  - 未設定だと `actions/deploy-pages` が `404 Not Found` で失敗します。

### ローカルでHTML生成

```bash
python3 scripts/build_pages.py
```

生成物は `dist/index.html` です。

### GitHub Actions（CI）での注意

- Ubuntu上で `ImportError: libSDL2-2.0.so.0` が出る場合はSDL2不足が原因です（workflowで `libsdl2-2.0-0` を導入します）。
- Web版は環境によって日本語フォント描画（`Pillow`）が使えないため、文字が `???` になることがあります。その場合はWeb版だけ英語表示にフォールバックします（日本語はローカル実行で表示できます）。
  - 強制的に英語にする: `GAME_LANG=en`

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
