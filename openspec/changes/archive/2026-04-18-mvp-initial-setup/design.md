## Context

AIコーディングツール用の設定ファイル（CLAUDE.md, .codex/rules, .cursor/rules等）を自動生成するWebアプリケーションの新規構築。ユーザーはウィザード形式で質問に回答し、結果をプレビュー・編集してZIPダウンロードする。

現状コードは空の状態。フロントエンド（React SPA）とバックエンド（FastAPI API）をモノレポ構成で構築する。

## Goals / Non-Goals

**Goals:**

- ウィザード入力 → テンプレート生成 → プレビュー → ダウンロードの一連のフローを実現
- プリセットによるクイックスタート
- 3秒以内のレスポンスタイム
- フロントエンド・バックエンドの明確な責務分離

**Non-Goals:**

- GitHub連携（直接Push）
- リポジトリ診断
- チーム共有・マルチテナント
- SSO / OAuth認証（MVPではシンプルなメール+パスワード認証）
- モバイル対応
- 多言語対応（日本語のみ）
- テンプレートバージョン管理

## Decisions

### 1. モノレポ構成

```
harness_builder/
├── frontend/      # React SPA (Vite + TypeScript + Tailwind + Shadcn)
├── backend/       # FastAPI backend
│   └── templates/ # Jinja2テンプレート
├── pgsql/         # PostgreSQLのconfigファイル
├── docker-compose.yml
└── ...
```

**理由**: フロントエンドとバックエンドが密結合な機能（ウィザード→生成→プレビュー）のため、モノレポが開発効率に優れる。docker-composeで各サービスをコンテナ化し、一括管理する。

**代替案**: 別リポジトリ → MVPフェーズでは管理コストが増すだけ。

### 2. テンプレートエンジン: Jinja2

ファイル生成にJinja2テンプレートを使用。テンプレートファイルは `backend/templates/` に配置し、カテゴリ別にディレクトリ分割する。

```
backend/templates/
├── agent_rules/     # AGENTS.md, PROJECT_RULES.md
├── tool_configs/    # CLAUDE.md, .codex/rules, .cursor/rules
├── prompts/         # feature.md, bugfix.md, review.md
├── quality/         # definition_of_done.md, review_checklist.md, test_strategy.md
└── scripts/         # verify.sh
```

**理由**: REQUIREMENTS.mdで指定済み。テンプレートの可読性が高く、非エンジニアでもテンプレートの修正が容易。

**代替案**: 文字列テンプレート → 保守性が低い。LLMによる動的生成 → レスポンスタイム要件（3秒以内）を満たせないリスク。

### 3. 認証: シンプルなセッション認証

MVPでは email + パスワードによるシンプルな認証。FastAPIのセッションミドルウェアを使用。

**理由**: MVPの機能スコープに認証の高度な要件がない。最短で実装可能。

**代替案**: JWT → SPAとの相性は良いがMVPでは過剰。OAuth → SSO対応はMVP外。

### 4. データベース設計

```sql
users (id, email, password_hash, created_at)
projects (id, user_id, name, preset_id, created_at, updated_at)
questionnaire_answers (id, project_id, question_key, answer_value)
generated_files (id, project_id, file_path, content, created_at, updated_at)
```

**理由**: REQUIREMENTS.mdのデータモデルに準拠。questionnaire_answersをキーバリュー形式にすることで、質問項目の追加に柔軟に対応。

### 5. API設計

RESTful APIとして設計。主要エンドポイント:

- `POST /api/v1/auth/register` — ユーザー登録
- `POST /api/v1/auth/login` — ログイン
- `POST /api/v1/projects` — プロジェクト作成
- `PUT /api/v1/projects/{id}/answers` — ウィザード回答保存
- `POST /api/v1/projects/{id}/generate` — ファイル生成実行
- `GET /api/v1/projects/{id}/files` — 生成ファイル一覧取得
- `GET /api/v1/projects/{id}/files/{file_id}` — ファイル内容取得
- `PUT /api/v1/projects/{id}/files/{file_id}` — ファイル編集
- `GET /api/v1/projects/{id}/export` — ZIPダウンロード
- `GET /api/v1/presets` — プリセット一覧

### 6. フロントエンドルーティング

React Router v6を使用。

- `/` — ランディング / ダッシュボード
- `/projects/new` — ウィザード（ステップ形式）
- `/projects/:id` — プロジェクト詳細（プレビュー・編集）
- `/projects/:id/export` — エクスポート確認

## Risks / Trade-offs

- **[テンプレート品質]** Jinja2テンプレートの品質がサービス価値に直結する → 主要プリセット（FastAPI+React）のテンプレートを優先的に品質担保し、段階的に拡充
- **[スケーラビリティ]** questionnaire_answersのキーバリュー設計はクエリ効率が低い → MVPのデータ量では問題にならない。将来的にJSONBカラムへの移行を検討
- **[セキュリティ]** セッション認証はCSRF対策が必要 → SPA + APIの構成ではCORSとCSRFトークンで対応
- **[ZIP生成の負荷]** 大量ファイルのZIP生成はサーバー負荷になりうる → MVPでは10〜15ファイル程度のため問題なし

