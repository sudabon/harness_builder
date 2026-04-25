## ADDED Requirements

### Requirement: Alembic履歴を単一の正規経路として管理する

システムは、データベーススキーマの作成と更新にAlembicのrevision履歴を正規経路として使用しなければならない（MUST）。履歴は単一の `head` を持ち、分岐したheadを残してはならない（MUST NOT）。

#### Scenario: 単一headの確認
- **WHEN** 開発者がAlembicの履歴状態を確認する
- **THEN** revision graph は単一の `head` を示し、複数headや未解決の分岐を含まない

#### Scenario: クリーンDBへの適用
- **WHEN** クリーンなデータベースに `alembic upgrade head` を実行する
- **THEN** `users`, `projects`, `questionnaire_answers`, `generated_files`, `alembic_version` の各テーブルが作成される

### Requirement: マイグレーション後スキーマはSQLAlchemyモデルと整合する

システムは、Alembic適用後のスキーマがSQLAlchemyモデルで定義されたテーブル、カラム、外部キー、ユニーク制約、インデックスと整合することを検証できなければならない（MUST）。

#### Scenario: モデル定義との整合確認
- **WHEN** マイグレーションを適用したデータベースのスキーマを検査する
- **THEN** 主要テーブルのカラム、外部キー、ユニーク制約、インデックスは現在のSQLAlchemyモデル定義と一致する

#### Scenario: 既存スキーマ互換性の維持
- **WHEN** マイグレーション整理後に既存APIテストを実行する
- **THEN** ユーザー登録、プロジェクト作成、回答保存、ファイル生成、ファイル編集、ZIPエクスポートの既存フローは従来通り成功する

### Requirement: テスト環境はマイグレーション経由のスキーマを検証する

システムは、テスト環境で少なくとも1つの自動テストによりAlembicマイグレーション適用結果を検証しなければならない（MUST）。テストは新規外部依存なしで実行できなければならない（MUST）。

#### Scenario: テスト用DBへのマイグレーション適用
- **WHEN** バックエンドテストがテスト用データベースを準備する
- **THEN** Alembic revision履歴を使ってスキーマを作成または検証できる

#### Scenario: マイグレーション検証の失敗
- **WHEN** Alembic revisionがモデルに必要なテーブルまたは制約を作成しない
- **THEN** マイグレーション検証テストは失敗し、スキーマ不整合を検知できる
