# 2D縦スクロール・ジャンピングゲーム（pyxel）仕様

このリポジトリは `../2d_game`（pygame版）の仕様を踏襲し、pyxelで再実装したものです。

## ゲームの目的（プレイヤ体験）

- 足場を渡って上方向へ登り続け、最高到達「階層（floor）」を伸ばす。
- 下から水位が迫り、遅いと水没してゲームオーバーになる。
- 敵を踏みつけ撃破すると、シェイク/ヒットストップ/パーティクル/SEで気持ちよさを出す。
- アイテムで短時間の強化（速度/ジャンプ/すり抜け/無敵/最大HP+1）。
- 開始時の“番人”との対話で雰囲気プロンプトを作り、テーマ（配色・形・名称）を変える。

## 操作

- ← / →: 移動
- Space（または Z）: ジャンプ（長押しで貯め、離して発射）
- Enter: 決定
- Esc: 戻る（タイトルでは終了）

## 追加仕様（pyxel版の拡張）

### 水面の描画

- 水位は「水の面（ライン+波）」と「水の中（塗り）」を描画する。

### 設定可能な閾値

- 落下によるゲームオーバー判定（画面下にどれだけ落ちたら終了するか）を環境変数で設定できる。
  - `GAME_FALL_BELOW_SCREEN_PX`（デフォルト: 画面高の0.8倍）
- ジャンプ時にスクロール（カメラ追従）が開始する「プレイヤの画面内Y座標（px）」を設定できる。
  - `GAME_SCROLL_START_PLAYER_SCREEN_Y`（デフォルト: 画面高の0.60倍）
- 水位の初期位置と上昇速度を環境変数で設定できる。
  - `GAME_WATER_START_OFFSET`（デフォルト: 1100px）
  - `GAME_WATER_BASE_SPEED`（デフォルト: 42px/s）
  - `GAME_WATER_SPEED_PER_FLOOR`（デフォルト: 0.55px/s per floor）

### 文字サイズ

- UI/会話/ランキング等は日本語フォントをラスタライズして描画し、文字サイズを大きめにする。

### 階層（バイオーム）背景

階層に応じて淡い背景色のドット絵に切り替える。イメージ:

1. 砂浜
2. 道路
3. 村
4. 町
5. 山
6. 富士山
7. 空
8. 宇宙
9. 月
10. 火星
11. 天国

### 階層の移り変わり演出

- 背景（バイオーム）が切り替わった瞬間に効果音を鳴らす。
- バイオーム名を一瞬大きく表示（ポップ）してから通常サイズに戻す。

## 既知の注意（アイテムと当たり判定）

- 「すり抜け（phase）」は敵との衝突を無効化し、横方向は画面端でワープする。
- 足場は常に当たり判定を持ち、アイテム取得直後に床をすり抜けて落ちる事故を防ぐ。

## コアゲームループ

1. 入力処理（左右 + ジャンプ貯め/発射）
2. 物理更新（重力、衝突、摩擦、最大速度）
3. カメラ更新（上方向に追従）
4. 生成（足場、アイテム、敵）
5. 判定（アイテム取得、敵との衝突/踏みつけ、無敵/すり抜け）
6. UI（水位、HP、階層）
7. 演出（撃破シェイク/ヒットストップ/パーティクル/SE）
8. ゲームオーバー判定（落下、水没、HP0）

## スコア（階層）

- `floor = int((start_y - min_y) / FLOOR_HEIGHT_PX)` として最高到達を整数化。

## タイムプレッシャー（水位）

- 水位は時間と階層に応じた速度で上昇（画面下→上へ迫る）。
- 水位が近いと警告SE。

## キャラクタ生成（ローディング）

- 番人の入力完了後、ローディングバーを表示しつつキャラクタ外見を生成。
- `GAME_CHARACTER_GENERATE_CMD` があれば外部コマンドで `save/generated_character.json` を生成し、失敗時は決定論フォールバック。
- キャラクタごとに特性が変わる（移動速度、ジャンプ力、ジャンプチャージ速度、HP、重力）。

## 永続化

- `save/highscore.json`: ハイスコア
- `save/runs.json`: 直近100件の記録（ランキング用）

## GitHub Pages（HTML出力）でプレイできるようにする計画

目的: GitHub ActionsでHTML版をビルドしてArtifacts化し、GitHub Pagesにデプロイしてブラウザでプレイ可能にする。

### 前提

- pyxelのHTML出力（WebAssembly/Emscripten）機能を利用する。
- GitHub Pagesは `gh-pages` ブランチ、または `actions` のPagesデプロイ（`pages`）を利用する。
- ランタイム保存（ハイスコア等）はブラウザ側の制約があるため、最初は「保存なし/揮発」でも良い（必要なら後でlocalStorage等へ対応）。

### 実装ステップ

1. ローカルでHTMLビルド手順を確立
   - `pyxel` が提供するビルドコマンド（例: `pyxel app2html`）でHTMLを生成する。
     - `pyxel app2html <app.pyxapp>` は内部的に `pyxel.js` の `launchPyxel({ gamepad: "enabled", ... })` を使う（仮想ゲームパッド表示に対応）。
   - もしくはHTMLを手書きする場合は、`pyxel.js` を読み込んで以下の形式で埋め込む:
     - `<pyxel-run root="." name="main.py" gamepad="enabled"></pyxel-run>`
     - `<pyxel-play root="." name="main.pyxapp" gamepad="enabled"></pyxel-play>`
   - 生成物（`index.html` と wasm/js/asset群）がGitHub Pagesの静的ホスティングで動くことを確認する。
   - 入口は `python -m game` 相当（`game/app.py`）をHTMLビルド対象にする。

2. 出力ディレクトリとignoreを整備
   - `dist/` をビルド成果物置き場にする。
   - `dist/` はgit管理しない（`.gitignore` 済み）。

3. GitHub Actions ワークフローを追加
   - `.github/workflows/pages.yml` を追加し、以下を行う:
     - Pythonセットアップ（推奨: 3.11）
     - `pip install -r requirements.txt`
     - HTMLビルドコマンドを実行（`dist/` へ出力）
     - `actions/upload-pages-artifact` で `dist/` をアップロード
     - `actions/deploy-pages` でデプロイ

4. Pages設定を有効化
   - リポジトリ設定で GitHub Pages のSourceを `GitHub Actions` に設定する。

5. READMEに公開URLとビルド方法を追記
   - ローカルでのHTML出力手順、GitHub PagesのURL、既知の制約（保存/音周りなど）を追記する。

### 受け入れ条件

- `main` へのpush（または手動実行）でGitHub Actionsが成功し、GitHub Pagesに `index.html` がデプロイされる。
- ブラウザ上で起動し、タイトル→番人→ローディング→ステータス→プレイ→ゲームオーバーまで一連が動作する。

### 既知の注意（Web/モバイル）

- `gamepad="enabled"` は `pyxel.js` 側の仮想ゲームパッド（タッチUI）表示であり、**ゲーム本体がWebで動くこと**とは別問題。
- 本プロジェクトは日本語描画に `Pillow` を使っているため、Pyodide環境（`<pyxel-run>`）での動作可否は要検証。Web向けには「Pillow不要な描画手段」へ寄せるか、Webビルド方式を `pyxel app2html` に統一して検証する。
- GitHub Actions（Ubuntu）で `ImportError: libSDL2-2.0.so.0` が出る場合は、pyxelのネイティブモジュールがSDL2ランタイムに依存しているのが原因。
  - 対策: workflowに `apt-get install -y libsdl2-2.0-0` を追加してから `pip install` / ビルドを実行する。

## ゲームパッド対応（計画）

目的: キーボードに加えてゲームパッドでもプレイ/操作できるようにする（ローカル/HTML両方を想定）。

### 対応範囲（最低限）

- 左右移動: 十字キー左右、または左スティックX
- ジャンプ: Aボタン相当（例: ボタン0）
- 決定: A（ジャンプと同一でも可）
- 戻る: Bボタン相当（例: ボタン1）

### 実装方針

- `game/input.py` にゲームパッド入力の読み取りを追加し、既存の `InputState` に統合する。
- pyxelのゲームパッドAPI（例: `pyxel.btn()` の `GAMEPAD1_BUTTON_*` / `GAMEPAD1_AXIS_*` / `GAMEPAD1_DPAD_*`）を利用する。
- 軸入力はデッドゾーン（例: 0.25）を設け、左右同時入力は相殺する。
- HTML版でもブラウザのGamepad API経由で動く前提で、キーボードと同様に使えることを目標とする（環境差がある場合はREADMEに既知事項として記載）。

### 追加設定（任意）

- デッドゾーン調整: `GAME_GAMEPAD_DEADZONE`
- ボタン割り当て調整（必要になったら）: `GAME_GAMEPAD_JUMP_BTN` 等

### 受け入れ条件

- タイトル/番人/ステータス/ゲーム中/ゲームオーバーの全シーンで、ゲームパッドのみで一連操作が可能。
- 左スティックの微小入力で勝手に移動しない（デッドゾーンが効く）。
