# Harness Builder

AI コーディングエージェント向けの運用ルール（ハーネス）を、質問票とプリセットから OpenSpec change パッケージとして生成する Web アプリケーションです。ログインしたユーザーがプロジェクトを作成し、回答を保存したうえで Jinja2 テンプレートから `openspec/changes/setup-ai-harness/` を生成し、ブラウザで編集したあと ZIP でエクスポートできます。

## 主な機能

- **ユーザー認証**: メール・パスワードの登録／ログイン／ログアウト。セッション Cookie（`credentials: "include"`）で API と連携します。
- **プリセット**: FastAPI + React、Next.js、Python API、SaaS Web App など。選択すると質問の初期値が埋まります。
- **プロジェクトウィザード**: プロジェクト種別、言語、フレームワーク、利用 AI ツール、テスト・Lint、レビュー方針などのアンケートに回答します（必須項目はバックエンドでも検証されます）。
- **OpenSpec change 生成・編集**: 生成後に一覧・ツリー表示で開き、`proposal.md` や `tasks.md` を PUT で更新できます。
- **ZIP エクスポート**: 生成物をディレクトリ構造のままダウンロードし、対象リポジトリのルートに展開できます。

## 生成されるパッケージ

バックエンドの Jinja2 テンプレートから、主に次のような OpenSpec change パッケージが出力されます。従来のハーネス下書き（`AGENTS.md`、`CLAUDE.md`、`scripts/verify.sh` など）は `tasks.md` にインライン同梱され、`/opsx:apply setup-ai-harness` 実行時に対象リポジトリへ合わせて洗練・作成されます。

| 出力パス | 概要 |
| --- | --- |
| `openspec/changes/setup-ai-harness/proposal.md` | change の目的と影響 |
| `openspec/changes/setup-ai-harness/design.md` | change の技術設計・判断記録 |
| `openspec/changes/setup-ai-harness/tasks.md` | ハーネス作成タスクと参照下書き |
| `openspec/changes/setup-ai-harness/.openspec.yaml` | spec-driven change 設定 |
| `openspec/changes/setup-ai-harness/specs/ai-coding-harness/spec.md` | ハーネス capability の delta spec |

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

PostgreSQL（`docker-compose.yml` の `db` サービス）を起動してからバックエンドを実行します。接続先は `DATABASE_URL` で上書きできます。

```bash
cd backend
uv sync --group dev
# 必要に応じて接続先を変更
# export DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/harness_builder
uv run uvicorn app.main:app --reload --port 8000
```

起動時に SQLAlchemy の `create_all` が走ります。マイグレーション履歴の確認・適用は `backend/README.md` の Alembic 手順を参照してください。

主な環境変数（`app/core/config.py`）:

| 変数 | 説明 |
| --- | --- |
| `DATABASE_URL` | DB 接続文字列（未設定時はローカル PostgreSQL） |
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
| PUT | `/projects/{id}/answers` | アンケート回答の更新（既知キーは型・選択肢を検証し正規化して保存。不正時 400） |
| POST | `/projects/{id}/generate` | OpenSpec change 生成（ボディ `{"force": bool}` 省略時 `false`。必須回答が欠けると 400） |
| GET | `/projects/{id}/files` | 生成された change ファイル一覧（各項目に `is_edited` を含む） |
| GET/PUT | `/projects/{id}/files/{file_id}` | 生成された change ファイルの取得・更新（内容変更時のみ `is_edited: true`） |
| GET | `/projects/{id}/export` | ZIP ダウンロード |

ZIP は対象リポジトリのルートに展開し、対象リポジトリで `/opsx:apply setup-ai-harness` を実行します。

## フロントエンドのルーティング

| パス | 内容 |
| --- | --- |
| `/` | ランディング |
| `/auth` | ログイン・登録 |
| `/projects/new` | 新規プロジェクトウィザード（要ログイン） |
| `/projects/:id` | プロジェクト詳細・生成物の閲覧・編集（要ログイン） |

## 関連ドキュメント

- バックエンドの DB・Alembic 運用: [backend/README.md](backend/README.md)
- フロントエンドの開発手順: [frontend/README.md](frontend/README.md)
