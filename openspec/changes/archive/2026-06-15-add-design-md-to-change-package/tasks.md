# Tasks: add-design-md-to-change-package

## 1. バックエンド: design.md テンプレート（新規）

- [x] 1.1 `backend/app/templates/openspec/design.md.j2` を追加。先頭を `# Design: {{ change_name }}` とし、OpenSpec 標準セクション（`## Context` / `## Goals / Non-Goals` / `## Decisions` / `## Risks / Trade-offs` / `## Migration Plan` / `## Open Questions`）を持つ。`build_template_context` の既存変数（`change_name`・`project_name`・`project_kind`・`project_kind_label`・`project_kind_focus`・`languages_csv`・`frameworks_csv`・`ai_tools_csv`・`tests_csv`・`lint_csv`・`review_policy`・`branch_strategy`・`ci_command`・`deploy_constraints`・`security_requirements`・`prohibited_actions`・`failure_examples`・`naming_convention`）で埋める。空になりうる自由記述項目は `{{ x or "未設定" }}` でガードする
- [x] 1.2 文面を `/opsx:apply setup-ai-harness` 時に対象リポジトリへ合わせて洗練する前提の下書きとして記述する

## 2. バックエンド: 生成定義への追加

- [x] 2.1 `backend/app/services/generator.py` の `CHANGE_TEMPLATE_DEFINITIONS` に `TemplateDefinition("openspec/design.md.j2", f"{CHANGE_ROOT}/design.md")` を proposal の直後に追加する
- [x] 2.2 既存の preview/edit/ZIP/孤児削除/編集保護/force が `design.md` に対して無改修で動くことを確認する

## 3. バックエンド: テスト更新

- [x] 3.1 `backend/tests/test_generation.py` に `DESIGN_PATH = f"{CHANGE_ROOT}/design.md"` を追加し、`CHANGE_PACKAGE_PATHS` に含める
- [x] 3.2 `test_change_package_files_include_expected_openspec_content` に `design.md` の内容アサーション（`# Design: setup-ai-harness`・`## Context`・`## Decisions`、および回答値の埋め込み）を追加する
- [x] 3.3 `backend/tests/test_projects.py` の `CHANGE_PACKAGE_PATHS` に `f"{CHANGE_ROOT}/design.md"` を追加する
- [x] 3.4 件数・集合系テスト（生成 / エクスポート / 再生成 / 孤児削除 / 編集保護）が `design.md` 込みで通ることを確認する

## 4. フロントエンド: 生成物一覧の更新

- [x] 4.1 `frontend/src/pages/home-page.tsx` の生成物一覧に `openspec/changes/setup-ai-harness/design.md` を proposal の直後に追記する
- [x] 4.2 既存のフロントエンドテスト（vitest）がグリーンであることを確認する

## 5. ドキュメント

- [x] 5.1 `README.md` の生成物テーブルに `openspec/changes/setup-ai-harness/design.md`（change の技術設計・判断記録）の行を追加する

## 6. 検証

- [x] 6.1 バックエンド全テスト（pytest）とフロントエンドテスト（vitest）を実行しグリーンを確認する
- [x] 6.2 生成した change パッケージを OpenSpec 初期化済みリポジトリに展開し、`openspec validate setup-ai-harness` がパスすることを確認する
