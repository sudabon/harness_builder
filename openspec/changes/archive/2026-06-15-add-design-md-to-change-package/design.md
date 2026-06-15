## Context

`generate_project_change`（`backend/app/services/generator.py`）は `CHANGE_TEMPLATE_DEFINITIONS` に列挙したテンプレートをレンダリングして change パッケージを生成する。現状の列挙は `proposal.md` / `tasks.md` / `.openspec.yaml` / `specs/ai-coding-harness/spec.md` の4種で、`design.md` のテンプレート定義もテンプレートファイルも存在しない。

Jinja2 環境は `StrictUndefined` で、テンプレートが参照する変数は全て context に存在する必要がある。`build_template_context` は `design.md` で使う変数（`project_kind`・`languages_csv`・`review_policy` 等）を既に提供しているため、新規変数の追加は不要。

制約: 日本語のみ・PC専用（MVP）。change 名は固定 `setup-ai-harness`。

## Goals / Non-Goals

**Goals:**
- 生成 change パッケージに `design.md` を1ファイル追加し、`proposal.md` と同じ仕組み（テンプレ定義への追加）で生成する。
- `design.md` を OpenSpec 標準セクション構成にし、質問票コンテキストから自動生成する。
- 既存の preview/edit/ZIP/孤児削除/編集保護/force を改修なしで流用する。

**Non-Goals:**
- `design.md` の内容を AI で動的生成すること（テンプレ＋下書き方針を維持）。
- change 名の動的化や他テンプレートの再設計。
- 生成 change の `spec.md` を design.md に統合するなどの構成変更。

## Decisions

### D1: `CHANGE_TEMPLATE_DEFINITIONS` に1エントリ追加
`TemplateDefinition("openspec/design.md.j2", f"{CHANGE_ROOT}/design.md")` を proposal の直後に追加する。
- **理由**: 生成・永続化・孤児削除・編集保護は定義リスト駆動なので、エントリ追加だけで全機構が `design.md` に追従する。出力順は最終的にソートされるため、位置は可読性のための選択。
- **代替案**: `design.md` 専用の生成経路を別途用意 → 機構の二重化で却下。

### D2: `design.md` は OpenSpec 標準セクションをテンプレ化
Context / Goals・Non-Goals / Decisions / Risks・Trade-offs / Migration Plan / Open Questions を持つ Jinja2 テンプレートを追加し、`build_template_context` の既存変数で埋める。生成ファイルは他の生成物（`proposal.md` は `# Proposal:`、`spec.md` は `# Delta:`）に合わせて `# Design: {{ change_name }}` の H1 で始める。
- **理由**: 既存 `proposal.md.j2` と同じ変数で完結でき、`StrictUndefined` 下でも未定義変数が発生しない。
- 自由記述項目（`review_policy` 等、空になりうる）は `proposal.md.j2` 同様 `{{ x or "未設定" }}` でガードする。

### D3: `design.md` は「apply 時に洗練する下書き」として位置づける
`proposal.md` / `spec.md` と同様、`/opsx:apply setup-ai-harness` 時に対象リポジトリへ合わせて補完する前提の文面にする。

## Risks / Trade-offs

- [テストがパッケージのパス集合を厳密一致で検証する] → `CHANGE_PACKAGE_PATHS` を更新するだけで追従する（件数系テストは集合参照のため自動追従）。
- [`StrictUndefined` で未定義変数による生成失敗] → テンプレは `build_template_context` 提供済みの変数のみ参照し、`test_template_environment_rejects_missing_variables` の前提を壊さない。
- [生成 change が `openspec validate` を通らない] → `design.md` は OpenSpec で任意ファイルのため検証へ影響しない。生成物で validate を再確認する。

## Migration Plan

1. `design.md.j2` を追加 → `CHANGE_TEMPLATE_DEFINITIONS` にエントリ追加。
2. バックエンドテストの期待値（パス集合・内容）を更新。
3. フロントエンドの生成物一覧と README を更新。
4. pytest / vitest を緑化し、生成物で `openspec validate setup-ai-harness` を確認。

ロールバック: 本 change を revert すれば `design.md` 追加前へ戻る（DB スキーマ変更なし）。

## Open Questions

- 生成 change の `spec.md` も必須要件として spec に明文化するか（今回は `design.md` に focus し、別 change で検討）。
