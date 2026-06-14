# Capability: file-export

## Purpose

生成または編集したハーネスファイルを、個別コピーまたはZIPダウンロードで外部利用できるようにする。
## Requirements
### Requirement: ZIP形式で一括ダウンロードできる

システムは、生成された change パッケージのファイル群をZIPファイルとして一括ダウンロードできるようにしなければならない（MUST）。ZIPファイル内のディレクトリ構造は各ファイルの `file_path`（`openspec/changes/<name>/...` のパッケージ相対パス）を保持しなければならず（MUST）、対象リポジトリのルートに展開すると `openspec/changes/<name>/` が再現される。

#### Scenario: ZIPダウンロード
- **WHEN** ユーザーが「ZIPダウンロード」ボタンを押す
- **THEN** `GET /api/v1/projects/{id}/export` からZIPファイルがダウンロードされ、`openspec/changes/<name>/proposal.md` 等が正しいディレクトリ構造で含まれる

#### Scenario: 編集後のZIPダウンロード
- **WHEN** ユーザーがファイルを編集した後にZIPダウンロードする
- **THEN** 編集後の内容が反映されたZIPファイルがダウンロードされる

#### Scenario: リポジトリへの展開
- **WHEN** ダウンロードしたZIPを OpenSpec 初期化済みリポジトリのルートで展開する
- **THEN** `openspec/changes/<name>/` 配下にパッケージが配置され、`/opsx:apply <name>` の対象となる

### Requirement: ファイル単位でコピーできる

ユーザーは個別のファイル内容をクリップボードにコピーできる。

#### Scenario: ファイル内容のコピー
- **WHEN** ユーザーがファイルプレビュー画面で「コピー」ボタンを押す
- **THEN** そのファイルの内容がクリップボードにコピーされ、コピー完了のフィードバックが表示される

### Requirement: エクスポートサービス整理後もZIP互換性を維持する

システムは、ZIP作成処理の内部構造を整理しても、保存済み生成ファイルのパスと内容を変更せずにエクスポートしなければならない（MUST）。

#### Scenario: 保存済みファイルのZIP出力互換性
- **WHEN** 生成ファイルを持つプロジェクトでZIPエクスポートを実行する
- **THEN** ZIPには各生成ファイルの `file_path` がアーカイブ内パスとして含まれ、各ファイルの `content` がそのまま書き込まれる

#### Scenario: 編集後ファイルのZIP出力互換性
- **WHEN** ユーザーが生成ファイルを編集して保存した後にZIPエクスポートを実行する
- **THEN** ZIPには編集後の内容が含まれ、編集前の内容に戻らない

