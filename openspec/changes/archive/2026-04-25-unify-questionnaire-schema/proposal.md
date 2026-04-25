## Why

ウィザード回答のキー、必須項目、選択肢、型がフロントエンド・バックエンド・プリセット・生成処理に分散しており、項目追加や名称変更時に不整合が起きやすい。既存の回答JSON形式を維持したまま、質問定義を一元化して保守性と回帰検知を高める。

## What Changes

- ウィザード回答のフィールド名、型、必須/任意、選択肢、表示ラベルを表す正規の質問スキーマを定義する
- フロントエンドの初期値・ステップ表示・選択肢・必須バリデーションを正規スキーマから参照する
- バックエンドの回答保存・生成前必須チェック・プリセット定義が同じスキーマと整合するようにする
- 既存の `answers` payload 形状、保存形式、生成テンプレートの入力キーは維持する
- スキーマ不整合を検知するテストを追加する

## Capabilities

### New Capabilities

- `questionnaire-schema`: ウィザード回答フィールドの正規定義、型、必須性、選択肢、プリセット整合性を管理する

### Modified Capabilities

なし

## Impact

- 影響範囲: `frontend/src/pages/project-wizard-page.tsx`, `frontend/src/lib/types.ts`, `backend/app/schemas/project.py`, `backend/app/api/routes/projects.py`, `backend/app/core/presets.py`, `backend/app/services/generator.py`, 関連テスト
- API互換性: `PUT /api/v1/projects/{id}/answers` と `ProjectResponse.answers` のJSONオブジェクト形式は変更しない
- データ互換性: `questionnaire_answers.question_key` と `answer_value` の保存形式は変更しない
- 依存関係: 新規外部依存は追加しない
