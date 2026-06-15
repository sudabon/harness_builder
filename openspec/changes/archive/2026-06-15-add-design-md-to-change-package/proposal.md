# Proposal: add-design-md-to-change-package

## Why

OpenSpec の propose では、change パッケージに `proposal.md` / `design.md` / `tasks.md` / `spec.md` が揃うことが期待される。しかし本アプリの生成器（`generate_project_change`）が出力する change パッケージには `design.md` が含まれておらず、設計判断（Context / Decisions / Risks 等）を記録する場所が欠落している。生成物を propose 相当の完全な change にするため、`design.md` をパッケージに追加する。

## What Changes

- change パッケージの生成物に `openspec/changes/setup-ai-harness/design.md` を追加する。
- `design.md` は OpenSpec 標準セクション（Context / Goals・Non-Goals / Decisions / Risks・Trade-offs / Migration Plan / Open Questions）で構成し、質問票の回答コンテキスト（`project_kind`・`languages`・`frameworks`・`ai_tools`・`review_policy`・`branch_strategy`・`security_requirements` 等）から自動で埋める。
- 既存の `proposal.md` / `spec.md` と同様、対象リポジトリで `/opsx:apply setup-ai-harness` 実行時に洗練する前提の下書きとする。
- 生成物のプレビュー一覧（フロントエンド）と README の生成物一覧に `design.md` を追記する。

## Capabilities

### Modified Capabilities

- `file-generation`: 生成する change パッケージに `design.md` を必ず含める要件を追加し、パッケージ構成要件を更新する。

## Impact

- **Backend**:
  - `app/templates/openspec/design.md.j2`（新規）
  - `app/services/generator.py`（`CHANGE_TEMPLATE_DEFINITIONS` に `design.md` を追加）
- **Frontend**: `src/pages/home-page.tsx`（生成物一覧に `design.md` を追記）
- **Tests**: `tests/test_generation.py` / `tests/test_projects.py`（`CHANGE_PACKAGE_PATHS` と内容アサーションを更新）
- **Docs**: `README.md` の生成物テーブルに `design.md` の行を追加
