# Delta: file-export

## MODIFIED Requirements

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
