# Proposal: fix-artifact-generation-logic

## Why

Artifacts生成のビジネスロジックに4つの欠陥があり、ユーザーが意図しない成果物が生成・配布される。具体的には、(1) AIツール選択を変更して再生成しても不要になったファイルが残留しZIPに混入する、(2) `PUT /answers` がバリデーションを行わず不正値（小文字ツール名・未知の選択肢）が黙って保存され生成結果を狂わせる、(3) 質問票で選べる `playwright` が `verify.sh` で未対応のため検証スクリプトが機能しない、(4) ユーザーが手動編集したファイルが再生成で無警告に上書きされ編集内容が失われる。

## What Changes

- **孤児ファイル削除**: 再生成時、現在の回答で選択されないテンプレート由来の `generated_files` 行を削除する（例: `ai_tools` から Cursor を外すと `.cursor/rules/project.mdc` が一覧・ZIPから消える）
- **回答バリデーション**: `PUT /api/v1/projects/{id}/answers` で既存の `validate_known_answer_value` を用いた検証を行い、不正な選択肢・型はHTTP 400で拒否する。未知キーは後方互換のため従来どおり保存を許容する
- **verify.sh の playwright 対応**: `test_strategy` で playwright を選択した場合に実行可能なコマンドを `verify.sh` に出力する
- **手動編集保護**: `generated_files` に編集済みフラグを追加し、ユーザーが編集したファイルは再生成時にデフォルトで上書きしない。フロントエンドは編集済みファイルの存在を提示し、明示的な上書き再生成を選択できる

## Capabilities

### New Capabilities

（なし）

### Modified Capabilities

- `file-generation`: 再生成時の孤児ファイル削除要件、手動編集ファイルの保護要件、verify.sh のテストツール網羅要件を追加
- `questionnaire-schema`: 回答保存API（`PUT /answers`）における既知キーの値バリデーション要件を追加（未知キーの後方互換要件は維持）
- `file-preview`: 編集済みファイルの識別（編集済みフラグの保持・表示）要件を追加

## Impact

- **Backend**: `app/services/generator.py`（孤児削除・編集保護）、`app/api/routes/projects.py`（バリデーション組み込み）、`app/templates/scripts/verify.sh.j2`（playwright対応）、`app/db/models.py` + Alembicマイグレーション（`generated_files.is_edited` カラム追加）
- **API**: `PUT /answers` が不正値に対し400を返すようになる（**BREAKING**: 従来は任意の値を受理していた）。`POST /generate` のレスポンス・ファイル一覧から孤児ファイルが消える
- **Frontend**: `project-detail-page.tsx`（編集済み表示・上書き確認）、`file-editor.tsx`（編集保存時のフラグ連動）
- **DB**: `generated_files` テーブルへのカラム追加マイグレーション
- **Tests**: `tests/test_generation.py`、`tests/test_projects.py` への追加
