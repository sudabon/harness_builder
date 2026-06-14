# Delta: file-preview

## MODIFIED Requirements

### Requirement: 生成ファイルをブラウザ上でプレビューできる

システムは、生成された change パッケージのファイル一覧と各ファイルの内容をブラウザ上で表示しなければならない（MUST）。ファイルはツリー構造またはリスト形式で一覧表示し（`openspec/changes/<name>/proposal.md` 等）、選択したファイルの内容をコードビューアで表示する。あわせて、ダウンロードした change を対象リポジトリの `openspec/changes/` に展開し `/opsx:apply <name>` を実行する使い方を提示しなければならない（MUST）。

#### Scenario: ファイル一覧の表示
- **WHEN** ファイル生成が完了し、プロジェクト詳細ページを表示する
- **THEN** 生成された change パッケージのすべてのファイルがファイルパスとともに一覧表示される

#### Scenario: ファイル内容のプレビュー
- **WHEN** ユーザーがファイル一覧からファイルを選択する
- **THEN** そのファイルの内容がMarkdownまたはコードとしてシンタックスハイライト付きで表示される

#### Scenario: 使い方ガイドの表示
- **WHEN** プロジェクト詳細ページを表示する
- **THEN** 「ZIPを対象リポジトリのルートに展開する」「`/opsx:apply <name>` を実行する」の手順が提示される
