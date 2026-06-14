# Tasks: switch-output-to-openspec-change

## 1. バックエンド: change パッケージ用テンプレート（新規）

- [x] 1.1 `backend/app/templates/openspec/` を作成し、`proposal.md.j2` を追加（`# Proposal: setup-ai-harness` / `## Why` / `## What Changes` / `## Capabilities`(New: `ai-coding-harness`) / `## Impact`。回答コンテキスト（`project_name`・`project_kind`・`languages_csv` 等）を反映）
- [x] 1.2 `openspec.yaml.j2` を追加（`schema: spec-driven` ＋ `created: {{ created }}`。出力先 `.openspec.yaml`）
- [x] 1.3 `spec.md.j2` を追加（`# Delta: ai-coding-harness` ＋ `## ADDED Requirements`。`### Requirement:` と `#### Scenario:`(WHEN/THEN) を最低1組。出力先 `specs/ai-coding-harness/spec.md`）
- [x] 1.4 `tasks.md.j2` を追加。`rendered_files`（`[{output_path, content}]`）をループし、各ハーネスごとに1タスク＋下書きをフェンス付きコードブロックで同梱。各タスクに「下書きを土台に対象リポジトリの実情へ洗練・補完して作成。そのままコピーしない」を明記。末尾に検証タスク（`openspec validate`・lint・test）を出力

## 2. バックエンド: generator.py の2段レンダリング化

- [x] 2.1 `backend/app/services/generator.py` の `generate_project_files` 内の下書きレンダリングループを `_render_all_drafts(project, answers) -> list[RenderedTemplate]` に抽出（`build_template_context`・`_select_template_definitions`・`_render_template` を再利用）
- [x] 2.2 `CHANGE_NAME = "setup-ai-harness"` と change パッケージ用の出力パス定数（`openspec/changes/<name>/...`）を定義
- [x] 2.3 `generate_project_change(session, project, *, force=False) -> list[GeneratedFile]` を実装。手順: (a) `_render_all_drafts` で下書き取得 (b) change コンテキスト構築（`build_template_context` の戻り ＋ `change_name`・`created`（本日）・`rendered_files`） (c) `openspec/*.j2` をレンダリングし `file_path` を `openspec/changes/<name>/...` とした `RenderedTemplate` 群を生成 (d) `_upsert_generated_file`・`_delete_orphan_generated_files` を流用して永続化（force・編集保護・孤児削除を維持）
- [x] 2.4 `tasks.md.j2` に渡す `rendered_files` のパスがツール選択を反映していることを確認（`_select_template_definitions` 経由）

## 3. バックエンド: API エンドポイント切替

- [x] 3.1 `backend/app/api/routes/projects.py` の `POST /api/v1/projects/{id}/generate` を `generate_project_change` 呼び出しに差し替え（`force` の受け渡しは現行どおり）
- [x] 3.2 files 一覧・詳細・編集（PUT）・export エンドポイントが無改修で動くことを確認（`GeneratedFile` 行を列挙/ZIP化するのみ。`build_project_zip` は `file_path` をそのまま使用）

## 4. バックエンド: テスト更新

- [x] 4.1 `backend/tests/test_generation.py` の期待値を change パッケージへ更新（生成行に `openspec/changes/setup-ai-harness/proposal.md`・`tasks.md`・`.openspec.yaml` が含まれる）
- [x] 4.2 「`tasks.md` に各下書きがインライン同梱される」「Cursor 解除で `tasks.md` から該当下書きが消える」テストを追加
- [x] 4.3 編集保護（通常再生成で `is_edited` 行を保持）・force 上書き・孤児削除が change パッケージでも従来どおり動くテストを更新/追加
- [x] 4.4 `backend/tests/test_projects.py` の generate/export 期待値を更新（ZIP に `openspec/changes/<name>/...` レイアウトが含まれる）

## 5. フロントエンド: 文言・使い方ガイド

- [x] 5.1 `frontend/src/pages/project-detail-page.tsx` に「使い方」パネルを追加（①ZIP を対象リポジトリのルートに展開 → `openspec/changes/` が生成 ②`/opsx:apply setup-ai-harness` を実行）。既存のコピー/ZIP/編集/再生成 UI は流用
- [x] 5.2 `frontend/src/pages/home-page.tsx` の製品説明を「各種ファイルを ZIP で持ち帰る」から「OpenSpec change を生成 → `opsx:apply` で適用」に更新
- [x] 5.3 `frontend/src/pages/project-wizard/confirmation-step.tsx` の出力説明文言を change パッケージ生成に更新
- [x] 5.4 関連するフロントエンドのユニットテスト（vitest）を更新

## 6. ドキュメント

- [x] 6.1 `REQUIREMENTS.md` 4.2/4.4 のエクスポート記述を「フラットファイル＋ZIP」から「OpenSpec change パッケージ＋ZIP、対象リポジトリで `/opsx:apply`」に更新
- [x] 6.2 `backend/README.md` / `frontend/README.md` の生成・エクスポート説明を更新

## 7. 検証

- [x] 7.1 生成パッケージをスクラッチの `openspec/changes/<name>/` に書き出し、`openspec validate <name>` がパスすることを確認（不要なら `spec.md.j2` を外す判断もここで行う）
- [x] 7.2 バックエンド全テスト（pytest）とフロントエンドテスト（vitest）を実行しグリーンを確認
- [x] 7.3 docker-compose 環境で「ウィザード → 生成 → プレビュー（proposal/tasks 確認）→ ZIP DL → テスト用リポジトリのルートに展開 → `/opsx:apply setup-ai-harness`」の一連を手動確認し、対象リポジトリにハーネスが生成されることを確認
