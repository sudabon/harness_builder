# Delta: file-generation

## ADDED Requirements

### Requirement: change パッケージに design.md を含める

システムは、生成する change パッケージに `design.md` を含めなければならない（MUST）。`design.md` は OpenSpec 標準セクション（Context / Goals・Non-Goals / Decisions / Risks・Trade-offs / Migration Plan / Open Questions）で構成し、質問票の回答コンテキスト（プロジェクト種別・言語・フレームワーク・AIツール・レビュー方針・ブランチ戦略・セキュリティ要件等）を反映しなければならない（MUST）。`design.md` の `file_path` は `openspec/changes/<name>/design.md` とする。

#### Scenario: design.md の生成

- **WHEN** 必須回答が揃ったプロジェクトでファイル生成を実行する
- **THEN** `openspec/changes/<name>/design.md` が `generated_files` に保存され、Context・Decisions などのセクションと回答内容が反映される

#### Scenario: ツール選択に依存せず design.md を生成する

- **WHEN** AIツールの選択内容を変えてファイル生成を再実行する
- **THEN** いずれの選択でも `design.md` はパッケージに含まれる

## MODIFIED Requirements

### Requirement: 生成成果物は OpenSpec change パッケージとして構成する

システムは、ファイル生成時に最終ハーネスファイル群ではなく、対象リポジトリの `openspec/changes/<name>/` 配下に展開可能な OpenSpec change パッケージを構成し、各ファイルを `generated_files` に保存しなければならない（MUST）。パッケージは少なくとも `proposal.md`・`design.md`・`tasks.md`・`.openspec.yaml` を含み、必要に応じて `specs/<capability>/spec.md` を含む。各 `generated_files` 行の `file_path` は `openspec/changes/<name>/...` のパッケージ相対パスとする。

#### Scenario: change パッケージの保存

- **WHEN** 必須回答が揃ったプロジェクトでファイル生成を実行する
- **THEN** `openspec/changes/<name>/proposal.md`・`openspec/changes/<name>/design.md`・`openspec/changes/<name>/tasks.md`・`openspec/changes/<name>/.openspec.yaml` が `generated_files` に保存される

#### Scenario: 生成物が妥当な change である

- **WHEN** 生成された change パッケージを OpenSpec 初期化済みリポジトリの `openspec/changes/<name>/` に展開する
- **THEN** `openspec validate <name>` が成功する
