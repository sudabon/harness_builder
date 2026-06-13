# questionnaire-schema Specification

## Purpose
TBD - created by archiving change unify-questionnaire-schema. Update Purpose after archive.
## Requirements
### Requirement: 正規質問スキーマを定義する

システムは、ウィザード回答の全フィールドについて、キー、表示ラベル、入力型、必須/任意、選択肢、初期値を表す正規質問スキーマを定義しなければならない（MUST）。

#### Scenario: 必須フィールドの定義
- **WHEN** システムが正規質問スキーマを読み込む
- **THEN** `project_kind`, `languages`, `frameworks`, `ai_tools`, `test_strategy`, `lint_format`, `prohibited_actions`, `review_policy` が必須フィールドとして定義されている

#### Scenario: 任意フィールドの定義
- **WHEN** システムが正規質問スキーマを読み込む
- **THEN** `branch_strategy`, `ci_command`, `deploy_constraints`, `security_requirements`, `failure_examples`, `naming_convention` が任意フィールドとして定義されている

#### Scenario: 選択肢フィールドの定義
- **WHEN** システムが正規質問スキーマを読み込む
- **THEN** 選択式フィールドには既存ウィザードと同じ許可値が定義されている

### Requirement: 既存回答payloadとの互換性を維持する

システムは、正規質問スキーマを導入しても、既存の `answers` JSONオブジェクト形式、回答キー、DB保存形式を維持しなければならない（MUST）。

#### Scenario: 回答保存payloadの互換性
- **WHEN** クライアントが既存形式の `answers` オブジェクトを `PUT /api/v1/projects/{id}/answers` に送信する
- **THEN** システムは既存と同じ `questionnaire_answers.question_key` と `answer_value` 形式で回答を保存する

#### Scenario: 回答取得payloadの互換性
- **WHEN** クライアントがプロジェクト詳細を取得する
- **THEN** `ProjectResponse.answers` は既存と同じキーを持つJSONオブジェクトとして返される

#### Scenario: 未知キーの後方互換性
- **WHEN** 既存クライアントが正規質問スキーマに存在しない回答キーを送信する
- **THEN** システムは公開APIの互換性を破る拒否を行わず、既存保存フローを維持する

### Requirement: フロントエンドとバックエンドが同じ質問定義を参照する

システムは、ウィザード表示、初期値、必須バリデーション、バックエンド生成前チェック、生成コンテキスト作成に同じ正規質問定義を使用しなければならない（MUST）。

#### Scenario: フロントエンド初期値の生成
- **WHEN** ユーザーがプリセットなしでウィザードを開始する
- **THEN** フロントエンドは正規質問スキーマの初期値に基づいて空の回答状態を作成する

#### Scenario: 必須バリデーションの整合
- **WHEN** ユーザーが必須フィールドを未入力のまま生成前ステップへ進もうとする
- **THEN** フロントエンドとバックエンドは正規質問スキーマ上の同じ必須フィールドを不足として扱う

#### Scenario: 生成コンテキストの整合
- **WHEN** ファイル生成が実行される
- **THEN** 生成サービスは正規質問スキーマに基づいて配列型と文字列型の回答を正規化し、既存テンプレートキーへ渡す

### Requirement: プリセットは質問スキーマと整合する

システムは、すべてのプリセット回答が正規質問スキーマに定義されたキーと型に整合していることを検証できなければならない（MUST）。

#### Scenario: プリセットキーの整合確認
- **WHEN** プリセット定義を検証する
- **THEN** 各プリセットの `answers` に含まれるキーは正規質問スキーマに定義されたキーと一致する

#### Scenario: プリセット値の整合確認
- **WHEN** プリセット定義を検証する
- **THEN** 選択式フィールドの値は正規質問スキーマで許可された選択肢だけを含む

#### Scenario: プリセット適用の互換性
- **WHEN** ユーザーが既存プリセットを選択する
- **THEN** ウィザードには従来と同じ値が事前入力され、ユーザーは個別項目を変更できる

### Requirement: 回答保存APIで既知キーの値を検証する

システムは、`PUT /api/v1/projects/{id}/answers` で受信した回答のうち正規質問スキーマに定義されたキーについて、入力型と選択肢の妥当性を検証しなければならない（MUST）。検証エラーがある場合はHTTP 400を返し、いずれの回答も保存しない。未知キーは検証対象外とし、既存の後方互換要件（未知キーを拒否しない）を維持する。

#### Scenario: 不正な選択肢の拒否
- **WHEN** クライアントが `ai_tools: ["claude"]`（選択肢に存在しない小文字表記）を送信する
- **THEN** システムはHTTP 400を返し、エラー詳細に対象キーと理由を含め、回答は保存されない

#### Scenario: 型不一致の拒否
- **WHEN** クライアントが multi_choice フィールドにリスト以外の値、または single_choice / text フィールドに文字列以外の値を送信する
- **THEN** システムはHTTP 400を返し、回答は保存されない

#### Scenario: 正当な回答の保存
- **WHEN** クライアントが正規質問スキーマの選択肢・型に適合する回答を送信する
- **THEN** 回答は従来どおり保存され、HTTP 200で更新後のプロジェクトが返される

#### Scenario: 未知キーの後方互換
- **WHEN** クライアントが正規質問スキーマに存在しないキーを含む回答を送信する
- **THEN** 未知キーは検証されず従来どおり保存され、リクエストは拒否されない

