## 1. プロジェクト初期セットアップ

- [x] 1.1 モノレポ構成のディレクトリ作成（frontend/, backend/, pgsql/, docker-compose.yml）
- [x] 1.2 フロントエンド初期化（Vite + React + TypeScript + Tailwind CSS + Shadcn UI）
- [x] 1.3 バックエンド初期化（FastAPI + SQLAlchemy + Alembic + Jinja2）
- [x] 1.4 PostgreSQL接続設定とdocker-compose定義
- [x] 1.5 開発環境の動作確認（フロント・バックエンド・DB接続）

## 2. データベース設計・マイグレーション

- [x] 2.1 SQLAlchemyモデル定義（users, projects, questionnaire_answers, generated_files）
- [x] 2.2 Alembicマイグレーション作成・実行
- [x] 2.3 Pydanticスキーマ定義（リクエスト/レスポンス）

## 3. 認証API

- [x] 3.1 ユーザー登録エンドポイント（POST /api/v1/auth/register）
- [x] 3.2 ログインエンドポイント（POST /api/v1/auth/login）
- [x] 3.3 セッション管理ミドルウェア
- [x] 3.4 認証APIのテスト

## 4. プリセットAPI

- [x] 4.1 プリセットデータ定義（FastAPI+React / Next.js / Python API / SaaS Web App）
- [x] 4.2 プリセット一覧エンドポイント（GET /api/v1/presets）
- [x] 4.3 プリセットAPIのテスト

## 5. プロジェクト・ウィザードAPI

- [x] 5.1 プロジェクト作成エンドポイント（POST /api/v1/projects）
- [x] 5.2 ウィザード回答保存エンドポイント（PUT /api/v1/projects/{id}/answers）
- [x] 5.3 プロジェクト・回答APIのテスト

## 6. テンプレートエンジン・ファイル生成API

- [x] 6.1 Jinja2テンプレートディレクトリ構成作成
- [x] 6.2 エージェントルールテンプレート作成（AGENTS.md, PROJECT_RULES.md）
- [x] 6.3 ツール別設定テンプレート作成（CLAUDE.md, .codex/rules, .cursor/rules）
- [x] 6.4 作業テンプレート作成（prompts/feature.md, bugfix.md, review.md）
- [x] 6.5 品質管理テンプレート作成（definition_of_done.md, review_checklist.md, test_strategy.md）
- [x] 6.6 verify.shテンプレート作成
- [x] 6.7 ファイル生成エンドポイント（POST /api/v1/projects/{id}/generate）
- [x] 6.8 ファイル生成ロジックのテスト

## 7. ファイル取得・編集・エクスポートAPI

- [x] 7.1 生成ファイル一覧エンドポイント（GET /api/v1/projects/{id}/files）
- [x] 7.2 ファイル内容取得エンドポイント（GET /api/v1/projects/{id}/files/{file_id}）
- [x] 7.3 ファイル編集エンドポイント（PUT /api/v1/projects/{id}/files/{file_id}）
- [x] 7.4 ZIPエクスポートエンドポイント（GET /api/v1/projects/{id}/export）
- [x] 7.5 エクスポートAPIのテスト

## 8. フロントエンド：共通基盤

- [x] 8.1 React Router設定（/, /projects/new, /projects/:id）
- [x] 8.2 APIクライアント（fetch wrapper）作成
- [x] 8.3 認証コンテキスト・ログイン/登録ページ
- [x] 8.4 共通レイアウト（ヘッダー・ナビゲーション）

## 9. フロントエンド：ウィザード

- [x] 9.1 ウィザードコンテナコンポーネント（ステップ管理・状態管理）
- [x] 9.2 プリセット選択ステップ
- [x] 9.3 必須項目入力ステップ（種別・言語・FW・AIツール・テスト・Lint・禁止事項・レビュー方針）
- [x] 9.4 任意項目入力ステップ（ブランチ戦略・CI・デプロイ・セキュリティ・失敗事例・命名規約）
- [x] 9.5 確認・生成実行ステップ
- [x] 9.6 バリデーション実装（必須項目チェック）

## 10. フロントエンド：プレビュー・編集

- [x] 10.1 ファイル一覧コンポーネント（ツリー表示）
- [x] 10.2 ファイルプレビューコンポーネント（シンタックスハイライト）
- [x] 10.3 ファイル編集コンポーネント（テキストエディタ・保存・キャンセル）
- [x] 10.4 クリップボードコピー機能

## 11. フロントエンド：エクスポート

- [x] 11.1 ZIPダウンロードボタン・ダウンロード処理
- [x] 11.2 ダウンロード完了フィードバック

## 12. 結合テスト・動作確認

- [x] 12.1 ウィザード入力 → ファイル生成 → プレビュー → ダウンロードのE2Eフロー確認
- [x] 12.2 プリセット選択からのフロー確認
- [x] 12.3 ファイル編集後のZIPダウンロード確認
