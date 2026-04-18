## Why

AIコーディングツール（Claude Code / Codex / Cursor）を活用する開発者・チームが増える一方、ツールごとの設定ファイルやルール定義を手動で作成・管理する負担が大きい。設定の不備はAIの誤動作やコード品質の低下につながる。ウィザード形式の質問に答えるだけで、適切なハーネスファイルを一括生成できるWebアプリケーションを構築し、この課題を解決する。

## What Changes

- プロジェクト作成ウィザード（プロジェクト種別・言語・FW・AIツール等の入力フォーム）
- テンプレートエンジンによるハーネスファイル自動生成（CLAUDE.md, .codex/rules, .cursor/rules, プロンプトテンプレート等）
- 生成ファイルのプレビュー・簡易編集機能
- ZIP一括ダウンロード・ファイル単位コピー
- プリセット選択（FastAPI+React, Next.js, Python API, SaaS Web App）
- ユーザー認証・プロジェクト管理のデータ永続化

## Capabilities

### New Capabilities

- `project-wizard`: プロジェクト作成ウィザード。必須項目（種別・言語・FW・AIツール・テスト・Lint・禁止事項・レビュー方針）と任意項目の入力フォーム
- `file-generation`: テンプレートエンジンによるハーネスファイル生成。Jinja2テンプレートから各種設定ファイル・ルールファイルを生成
- `file-preview`: 生成ファイルのプレビュー表示と簡易テキスト編集機能
- `file-export`: ZIP一括ダウンロードとファイル単位コピー機能
- `presets`: プリセット選択機能。定義済みのプロジェクト構成を一発適用

### Modified Capabilities

（既存specなし。新規プロジェクトのため該当なし）

## Impact

- フロントエンド: React + TypeScript + Tailwind CSS + Shadcn UIで新規SPA構築
- バックエンド: FastAPI + Jinja2で新規API・テンプレートエンジン構築
- データベース: PostgreSQLにusers / projects / questionnaire_answers / generated_filesテーブル新設
- インフラ: マルチDockerコンテナサーバ / docker-compose.yamlで構築