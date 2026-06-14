## Context

現状、`POST /generate` は Jinja2 テンプレ（`app/services/generator.py` の `TEMPLATE_DEFINITIONS`）でハーネスファイル（`CLAUDE.md` 等）をレンダリングし、`generated_files` に1ファイル1行で保存している。プレビュー・編集・ZIP・孤児削除・編集保護（`is_edited`）・force 上書きはこの行集合に対して動く。

本変更は「成果物の届け方」を変える。最終ファイルではなく、対象リポジトリに展開して `/opsx:apply` できる **OpenSpec change パッケージ**を成果物とする。ハーネスの中身（テンプレ出力）は破棄せず、`tasks.md` に「参照下書き」として同梱し、apply 時に Claude が対象リポジトリの実情へ洗練する。

制約: 日本語のみ・PC専用（MVP）。`openspec` CLI v1.4.1 利用可。対象リポジトリは OpenSpec 初期化済み（`schema: spec-driven`）を前提とする。

## Goals / Non-Goals

**Goals:**
- `POST /generate` の成果物を change パッケージ（`proposal.md` / `tasks.md` / `.openspec.yaml` / `specs/ai-coding-harness/spec.md`）にする。
- テンプレ出力を `tasks.md` に下書き同梱し、apply 時に洗練される導線を作る。
- 既存の preview/edit/ZIP/孤児削除/編集保護/force を**そのまま再利用**する（影響最小）。
- 生成パッケージが `openspec validate` を通る。

**Non-Goals:**
- 一般（OpenSpec 非利用）ユーザー向けのフラット出力フォールバックは作らない。
- Claude API 連携は導入しない。
- 対象リポジトリの `openspec init` 自動化は範囲外（ドキュメントで前提化）。
- apply の自動実行は範囲外（ユーザーが手動で `/opsx:apply`）。

## Decisions

### D1: `GeneratedFile.file_path` を change パッケージ相対パスにする
成果物の各ファイルを `openspec/changes/<name>/proposal.md` のようなパスで `generated_files` に保存する。
- **理由**: preview（一覧/コードビューア）、ZIP（`build_project_zip` は `file_path` をそのままアーカイブパスに使用）、孤児削除（出力パス集合との差分）、編集保護（`is_edited`）が**一切改修なし**で機能する。ZIP をリポジトリのルートに展開すると `openspec/changes/<name>/` が再現される。
- **代替案**: 新しい専用テーブル／別エンドポイント → 既存機構を二重化し影響大。却下。

### D2: テンプレ出力は `tasks.md` にインライン同梱
各ハーネス下書きを、対応タスク本文にフェンス付きコードブロックで埋め込む。
- **理由**: `tasks.md` は `opsx:apply` が必ず読む context file。別ファイル（`drafts/`）だと apply が読む保証がない。インラインなら自己完結し archive 後も残る。
- **タスク文言**: 「下書きを土台に、対象リポジトリの実ディレクトリ構成・依存・既存規約へ洗練・補完して作成する。**そのままコピーしない**」を明示し、V3（意図＋制約＋下書き）の価値を担保。
- **代替案**: `design.md` 付録に集約 → 可読性は上がるがタスク単位の対応が薄れる。却下。

### D3: 生成パイプラインは2段レンダリング
`generator.py` で (1) 既存 `TEMPLATE_DEFINITIONS` から下書き群（`list[RenderedTemplate]`）を生成、(2) `app/templates/openspec/*.j2` に「回答コンテキスト＋下書き群＋change_name＋created」を渡して change パッケージをレンダリング。
- 既存 `build_template_context` / `_select_template_definitions` / `_render_template` を再利用。下書きレンダリングのループを `_render_all_drafts()` に抽出。
- 永続化は新 `generate_project_change()` が `_upsert_generated_file` / `_delete_orphan_generated_files` を流用。`POST /generate` はこれを呼ぶよう差し替え。

### D4: change 名は固定 `setup-ai-harness`
MVP では固定。将来プロジェクト名スラッグ付与を検討（Open Question）。

### D5: 出力 change の spec delta は最小 + validate 必須
`specs/ai-coding-harness/spec.md.j2` で「ハーネス一式を導入する」最小 delta（Requirement/Scenario）を出力。生成物に対し `openspec validate` を実行して妥当性を保証。validate 上 spec delta が不要と判明すれば `spec.md.j2` を外す。

## Risks / Trade-offs

- [apply が下書きをそのまま転記してしまう] → タスク文言で「コピー禁止・洗練必須」を強制。検証時に実 apply で確認。
- [出力 change が対象リポジトリのスキーマ（spec-driven 前提）と不一致] → 生成物を `openspec validate` で検証。前提を使い方ガイド/README に明記。
- [既存テストが flat 出力前提で全面赤化] → 振る舞い（orphan/force/編集保護）は不変。期待値（パス・内容）を change パッケージへ更新するのみでテスト構造は流用。
- [BREAKING な出力変更] → 個人・チーム用に全振りの方針で許容。`REQUIREMENTS.md` 4.2/4.4 を更新。

## Migration Plan

1. 新テンプレ追加 → `generator.py` 2段化 → `POST /generate` 差し替え。
2. 既存テストを change パッケージ期待値へ更新、新規テスト追加。
3. `openspec validate`（生成物）・pytest・vitest 緑化。
4. docker-compose で手動 E2E（ウィザード→生成→プレビュー→ZIP→対象リポジトリ展開→`/opsx:apply`）。
ロールバック: 本 change を revert すれば flat 出力へ戻る（DB スキーマ変更なし）。

## Open Questions

- change 名にプロジェクト名スラッグを付与すべきか（衝突回避 vs 単純さ）。MVP は固定で進める。
- 出力 change に spec delta を含めるか（validate 結果で確定）。
