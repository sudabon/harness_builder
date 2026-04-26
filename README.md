# Harness Builder

AI コーディングエージェント向けの運用ルール（ハーネス）を、質問票とプリセットから生成する Web アプリケーションです。ログインしたユーザーがプロジェクトを作成し、回答を保存したうえで Jinja2 テンプレートから複数ファイルを一括生成し、ブラウザで編集したあと ZIP でエクスポートできます。

## 主な機能

- **ユーザー認証**: メール・パスワードの登録／ログイン／ログアウト。セッション Cookie（`credentials: "include"`）で API と連携します。
- **プリセット**: FastAPI + React、Next.js、Python API、SaaS Web App など。選択すると質問の初期値が埋まります。
- **プロジェクトウィザード**: プロジェクト種別、言語、フレームワーク、利用 AI ツール、テスト・Lint、レビュー方針などのアンケートに回答します（必須項目はバックエンドでも検証されます）。
- **ファイル生成・編集**: 生成後に一覧・ツリー表示で開き、内容を PUT で更新できます。
- **ZIP エクスポート**: 生成物をディレクトリ構造のままダウンロードします。

## 生成されるファイルの例

バックエンドの Jinja2 テンプレートから、主に次のようなファイルが出力されます（利用ツールの回答に応じてツール固有ファイルはスキップされる場合があります）。

| 出力パス | 概要 |
| --- | --- |
| `AGENTS.md` | エージェント向けルール |
| `PROJECT_RULES.md` | プロジェクトルール |
| `CLAUDE.md` | Claude 向け（ツールに Claude が含まれる場合） |
| `.codex/rules/general.md` | Codex 向け |
| `.cursor/rules/project.mdc` | Cursor 向け |
| `prompts/*.md` | 機能・バグ修正・レビュー用プロンプト |
| `definition_of_done.md` など | 品質・レビュー・テスト方針 |
| `scripts/verify.sh` | 検証スクリプト |

## 技術スタック

| 層 | 技術 |
| --- | --- |
| フロントエンド | React 19、TypeScript、Vite 7、Tailwind CSS v4、React Router 7、Radix（Slot）ベースの UI コンポーネント |
| バックエンド | FastAPI、SQLAlchemy 2、Pydantic Settings、Jinja2、Starlette セッション、itsdangerous |
| データベース | PostgreSQL（Docker Compose 時）。ローカル単体では `DATABASE_URL` 未設定時に SQLite のデフォルトも利用可能 |
| マイグレーション | Alembic（スキーマの正史。モデル変更時はリビジョンとセットで管理） |

## 前提条件

- Docker と Docker Compose（推奨の一括起動）
- または: Python 3.11 以上（[uv](https://github.com/astral-sh/uv)）、Node.js、pnpm 10（`package.json` の `packageManager` に準拠）

## クイックスタート（Docker Compose）

```bash
docker compose up --build
```

| サービス | URL |
| --- | --- |
| フロントエンド | http://localhost:5173 |
| バックエンド API | http://localhost:8000（REST は `/api/v1` 配下） |
| ヘルスチェック | http://localhost:8000/healthz |
| PostgreSQL | ホストの `5432`（ユーザー `harness`、DB `harness_builder`） |

Compose ではフロントに `VITE_API_URL=http://localhost:8000/api/v1` が渡されます。バックエンドには `DATABASE_URL`、`FRONTEND_ORIGIN`、`SESSION_SECRET` が設定されます。

`pgsql/` は Postgres コンテナの `docker-entrypoint-initdb.d` にマウントされます。初期 SQL を置く場合はここに追加できます。

## ローカル開発（サービス単体）

### バックエンド

PostgreSQL を別途用意するか、SQLite で試す場合は `DATABASE_URL` を設定します。

```bash
cd backend
uv sync --group dev
# 例: PostgreSQL を使う場合
# export DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/harness_builder
uv run uvicorn app.main:app --reload --port 8000
```

起動時に SQLAlchemy の `create_all` が走ります。マイグレーション履歴の確認・適用は `backend/README.md` の Alembic 手順を参照してください。

主な環境変数（`app/core/config.py`）:

| 変数 | 説明 |
| --- | --- |
| `DATABASE_URL` | DB 接続文字列（未設定時は SQLite ファイル） |
| `SESSION_SECRET` | セッション署名用シークレット |
| `FRONTEND_ORIGIN` | CORS 許可オリジン（例: `http://localhost:5173`） |
| `SESSION_COOKIE_SECURE` | 本番など HTTPS 時は `true` を検討 |

### フロントエンド

```bash
cd frontend
pnpm install
# API の向き先（未設定時は http://localhost:8000/api/v1）
export VITE_API_URL=http://localhost:8000/api/v1
pnpm dev
```

### テスト

```bash
# バックエンド（pytest）
cd backend && uv run pytest

# フロントエンド（Vitest）
cd frontend && pnpm test

# E2E（Playwright）
cd frontend && pnpm test:e2e
```

## API の概要

プレフィックスは `/api/v1` です（認証系は Cookie セッション）。

| メソッド | パス | 説明 |
| --- | --- | --- |
| POST | `/auth/register` | ユーザー登録・セッション確立 |
| POST | `/auth/login` | ログイン |
| POST | `/auth/logout` | ログアウト |
| GET | `/auth/me` | 現在のユーザー |
| GET | `/presets` | プリセット一覧 |
| POST | `/projects` | プロジェクト作成 |
| GET | `/projects/{id}` | プロジェクト取得 |
| PUT | `/projects/{id}/answers` | アンケート回答の更新 |
| POST | `/projects/{id}/generate` | ファイル生成（必須回答が欠けると 400） |
| GET | `/projects/{id}/files` | 生成ファイル一覧 |
| GET/PUT | `/projects/{id}/files/{file_id}` | 生成ファイルの取得・更新 |
| GET | `/projects/{id}/export` | ZIP ダウンロード |

## フロントエンドのルーティング

| パス | 内容 |
| --- | --- |
| `/` | ランディング |
| `/auth` | ログイン・登録 |
| `/projects/new` | 新規プロジェクトウィザード（要ログイン） |
| `/projects/:id` | プロジェクト詳細・生成物の閲覧・編集（要ログイン） |

## 関連ドキュメント

- バックエンドの DB・Alembic 運用: [backend/README.md](backend/README.md)
