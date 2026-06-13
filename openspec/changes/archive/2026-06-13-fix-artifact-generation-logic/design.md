# Design: fix-artifact-generation-logic

## Context

ファイル生成は `app/services/generator.py` の `generate_project_files` が担う。`TEMPLATE_DEFINITIONS`（12テンプレート、うち3つは `required_tool` で AIツール選択に連動）を回答コンテキストでレンダリングし、`generated_files` テーブルへ upsert する。現状の問題:

- upsert のみで削除がなく、ツール選択を外しても旧ファイルが残留する（`_upsert_generated_file`）
- `PUT /answers` → `upsert_project_answers` は検証なしで保存する。`questionnaire.py` の `validate_known_answer_value` は実装済みだがテストからしか呼ばれていない
- `verify.sh.j2` は pytest / jest のみ対応で、質問票の選択肢にある playwright は「Skipping unsupported test tool」を出力する
- `PUT /files/{id}` でユーザーが編集した内容を、再生成が無条件に上書きする。編集済みかどうかの状態を持っていない

## Goals / Non-Goals

**Goals:**
- 再生成結果が常に「現在の回答から導かれるファイル集合」と一致する（孤児ゼロ）
- 不正な回答値をAPI境界で拒否し、生成ロジックに到達させない
- 質問票で選択可能な全テストツールが verify.sh で実行可能コマンドになる
- ユーザーの手動編集を再生成から保護し、上書きは明示的な操作に限定する

**Non-Goals:**
- テンプレート内容の質的改善（project_kind / languages による内容分岐）は別changeで扱う
- プリセット適用ロジックのバックエンド移管は扱わない
- ZIP内の実行権限付与（verify.sh の permission bit）は扱わない
- 編集内容と再生成結果のマージ・diff表示は行わない（保護 or 上書きの二択）

## Decisions

### D1: 孤児ファイルは「選択されなかったテンプレートの output_path」を削除する

`_select_template_definitions` の補集合（`TEMPLATE_DEFINITIONS` 全体 − 選択分）の `output_path` に一致する `generated_files` 行を削除する。全 `file_path` を一律削除して作り直す方式は、編集保護（D4）と両立しないため採らない。テンプレート定義に存在しない `file_path`（過去バージョンの遺物）も削除対象に含め、テーブルを常に現定義と整合させる。

### D2: バリデーションは route 層で `validate_known_answer_value` を呼ぶ

`update_answers` で受信 answers の各キーに対し既知キーのみ検証し、エラーがあれば HTTP 400（detail にエラー一覧）を返す。未知キーは questionnaire-schema の後方互換要件（未知キーを拒否しない）を維持するため素通しとする。`validate_preset_answers` は未知キーをエラーにするため流用せず、既知キー判定を加えた薄いラッパー `validate_answers_payload` を `questionnaire.py` に追加する。Pydantic スキーマでの検証は、質問定義（`QUESTIONNAIRE_FIELDS`）と二重管理になるため採らない。

### D3: verify.sh は playwright に `pnpm exec playwright test` を出力する

既存の jest / eslint / prettier が pnpm 前提のため、整合性を優先し pnpm で統一する。パッケージマネージャの選択化は質問票の変更を伴うためスコープ外。

### D4: 編集保護は `generated_files.is_edited` フラグ + 再生成スキップ

- DB: `generated_files` に `is_edited BOOLEAN NOT NULL DEFAULT FALSE` を追加（Alembicマイグレーション、既存行は FALSE）
- `PUT /files/{id}` で content 更新時に `is_edited = True` を設定
- 再生成時、`is_edited = True` の既存行は content を上書きせずスキップする（行は生成結果に含めて返す）
- `POST /generate` に `force: bool = False` ボディパラメータを追加。`force=True` で編集済みファイルも上書きし `is_edited` を False に戻す
- 孤児削除（D1）は `is_edited` に関わらず実行する。選択から外れたツールの設定ファイルは編集済みでも残す意味がないため
- レスポンス（`GeneratedFileSummaryResponse` / `GeneratedFileResponse`）に `is_edited` を含め、フロントは編集済みバッジ表示と、再生成ボタン押下時に編集済みファイルが存在する場合の確認ダイアログ（上書きする＝force / 保護したまま再生成）を実装する

代替案として「編集時に別テーブルへ退避」「生成内容とのdiffマージ」を検討したが、MVPの複雑度に見合わないため採らない。

## Risks / Trade-offs

- [400化による互換性破壊] 既存クライアントが不正値を送っていた場合に失敗し始める → フロントは正規の選択肢のみ送る実装のため実害は限定的。エラー detail にキー別の理由を含め復旧を容易にする
- [編集済みファイルが回答変更に追従しない] 回答を変えても編集済みファイルは古い内容のまま → 仕様として明示し、フロントの編集済みバッジと force 再生成で解決手段を提供する
- [孤児削除が編集済みファイルも消す] ツール選択を外すと編集済みでも削除される → 確認ダイアログの文言で削除されるファイルを提示する（フロント側で生成前に差分提示）
- [pnpm 固定] npm/yarn プロジェクトでは verify.sh が動かない → 既存挙動と同等であり本changeでは悪化しない

## Migration Plan

1. Alembic マイグレーション追加（`is_edited` カラム、DEFAULT FALSE、ロールバックは drop column）
2. バックエンド実装 → テスト → フロントエンド実装の順に同一PRで適用
3. ロールバック時はマイグレーションのみ downgrade すればアプリは旧コードで動作する（カラム追加のみのため前方互換）

## Open Questions

- なし（force 再生成のUI文言は実装時にフロントで確定する）
