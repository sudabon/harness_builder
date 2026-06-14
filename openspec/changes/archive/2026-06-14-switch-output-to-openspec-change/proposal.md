# Proposal: switch-output-to-openspec-change

## Why

品質向上のためにハーネス内容を Claude API で生成する案は従量課金が発生する。これを避けつつ品質を上げるため、本アプリの成果物を「最終ファイルのフラット生成＋ZIP」から **OpenSpec change パッケージの生成**に切り替える。ユーザーは生成された change を対象リポジトリの `openspec/changes/` に展開し、手元の Claude Code で `/opsx:apply` を手動実行する。実装はユーザーのサブスク内で走るため **API 課金ゼロ**で、生成物（ハーネス）は対象リポジトリへ**直接書き出される**（コピペの往復が不要）。質問票・プリセット・生成内容そのもの（提供価値）は維持する。

## What Changes

- **BREAKING（出力形式）**: `POST /generate` の成果物と ZIP の中身を、フラットなハーネスファイル群（`CLAUDE.md` 等）から、OpenSpec change パッケージ（`openspec/changes/setup-ai-harness/` 配下の `proposal.md` / `tasks.md` / `.openspec.yaml` / `specs/ai-coding-harness/spec.md`）に変更する。
- 現行 Jinja2 テンプレ出力は破棄せず、**「参照下書き」として `tasks.md` にインライン同梱**する。各タスクは「下書きを土台に、対象リポジトリの実情へ洗練・補完して作成する（そのままコピーしない）」と明示する。
- AI ツール選択（Claude/Codex/Cursor）は従来どおり「どの下書きを同梱するか」に反映する。
- 生成パッケージは `openspec validate` を通る妥当な spec-driven change とする。
- フロントエンドはプレビュー対象を change パッケージのファイルに更新し、「ZIP 展開 → `/opsx:apply` 実行」の使い方ガイドを提示する。製品説明文言も更新する。

## Capabilities

### New Capabilities

（なし。既存 capability の出力形式変更で対応する）

### Modified Capabilities

- `file-generation`: 生成成果物を OpenSpec change パッケージに変更し、テンプレ出力を `tasks.md` への下書き同梱として扱う要件を追加。AI ツール選択が同梱下書きの取捨に反映される要件は維持。
- `file-export`: ZIP の中身を、対象リポジトリのルートに展開すると `openspec/changes/<name>/` を構成するディレクトリレイアウトにする要件に変更。
- `file-preview`: プレビュー対象を change パッケージ内ファイル（`proposal.md` / `tasks.md` 等）とする要件に変更。編集済みフラグの保持・表示は維持。

## Impact

- **Backend**:
  - `app/templates/openspec/*.j2`（新規: `proposal.md.j2` / `tasks.md.j2` / `openspec.yaml.j2` / `spec.md.j2`）
  - `app/services/generator.py`（下書きレンダリング抽出 ＋ `generate_project_change` 追加。`_upsert_generated_file` / `_delete_orphan_generated_files` / force・編集保護は流用）
  - `app/api/routes/projects.py`（`POST /generate` を `generate_project_change` 呼び出しに切替）
  - `app/services/export.py`（`file_path` が change 相対パスになるため原則変更なし）
- **Frontend**: `pages/project-detail-page.tsx`（使い方ガイド追加）、`pages/home-page.tsx` / `pages/project-wizard/confirmation-step.tsx`（製品説明文言の更新）
- **Tests**: `tests/test_generation.py` / `tests/test_projects.py`（出力パス・内容の期待値更新。orphan削除・force・編集保護の振る舞いは不変のためテスト構造を流用）
- **Docs**: `REQUIREMENTS.md` 4.2/4.4 のエクスポート記述（フラットZIP → change パッケージ）を更新
