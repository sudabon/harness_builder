# Delta: file-generation

## ADDED Requirements

### Requirement: 生成成果物は OpenSpec change パッケージとして構成する

システムは、ファイル生成時に最終ハーネスファイル群ではなく、対象リポジトリの `openspec/changes/<name>/` 配下に展開可能な OpenSpec change パッケージを構成し、各ファイルを `generated_files` に保存しなければならない（MUST）。パッケージは少なくとも `proposal.md`・`tasks.md`・`.openspec.yaml` を含み、必要に応じて `specs/<capability>/spec.md` を含む。各 `generated_files` 行の `file_path` は `openspec/changes/<name>/...` のパッケージ相対パスとする。

#### Scenario: change パッケージの保存
- **WHEN** 必須回答が揃ったプロジェクトでファイル生成を実行する
- **THEN** `openspec/changes/<name>/proposal.md`・`openspec/changes/<name>/tasks.md`・`openspec/changes/<name>/.openspec.yaml` が `generated_files` に保存される

#### Scenario: 生成物が妥当な change である
- **WHEN** 生成された change パッケージを OpenSpec 初期化済みリポジトリの `openspec/changes/<name>/` に展開する
- **THEN** `openspec validate <name>` が成功する

### Requirement: ハーネス内容をテンプレ下書きとして tasks.md に同梱する

システムは、従来テンプレート（エージェントルール・ツール別設定・作業テンプレート・品質管理・実行補助）でレンダリングしたハーネス内容を、最終ファイルとしてではなく `tasks.md` の各タスク本文にフェンス付きコードブロックの「下書き」として同梱しなければならない（MUST）。各タスクは、下書きを土台に対象リポジトリの実情へ洗練・補完して作成すること、下書きをそのまま転記しないことを明示しなければならない（MUST）。選択された AI ツール（Claude/Codex/Cursor）に応じて、同梱するツール別設定の下書きを取捨する。

#### Scenario: 下書きの同梱
- **WHEN** ファイル生成を実行する
- **THEN** `tasks.md` に各ハーネス（`CLAUDE.md` 等）の下書きがコードブロックで埋め込まれ、「下書きを土台に洗練し、そのままコピーしない」旨の指示が各タスクに含まれる

#### Scenario: ツール選択に応じた下書きの取捨
- **WHEN** AI ツールとして Claude のみを選択してファイル生成を実行する
- **THEN** `tasks.md` に `CLAUDE.md` の下書きが含まれ、`.codex/rules/general.md` や `.cursor/rules/project.mdc` の下書きは含まれない

## MODIFIED Requirements

### Requirement: ウィザード回答からハーネスファイルを生成する

システムはウィザードの回答内容に基づき、Jinja2テンプレートエンジンを使用して OpenSpec change パッケージを生成しなければならない（MUST）。生成はAPIリクエストにより実行され、成果物（パッケージ内の各ファイル）は `generated_files` テーブルに保存される。

#### Scenario: ファイル生成の実行
- **WHEN** ユーザーがウィザード完了後に「生成」ボタンを押す
- **THEN** `POST /api/v1/projects/{id}/generate` が呼ばれ、回答に基づく change パッケージのファイル群が `generated_files` テーブルに保存される

#### Scenario: 生成完了の応答
- **WHEN** ファイル生成が正常に完了する
- **THEN** 3秒以内にレスポンスが返り、生成された change パッケージのファイル一覧が含まれる

### Requirement: 生成サービス整理後も生成互換性を維持する

システムは、サービス層の内部構造を整理しても、ウィザード回答とテンプレート定義から生成されるハーネス下書きの内容、およびAIツール選択に応じた取捨条件を維持しなければならない（MUST）。下書きは change パッケージの `tasks.md` に同梱される。

#### Scenario: 既存テンプレート出力の互換性
- **WHEN** 必須回答が揃ったプロジェクトでファイル生成を実行する
- **THEN** 選択されたAIツールと共通テンプレートに対応するハーネス下書きが、従来と同じ内容で `tasks.md` に同梱される

#### Scenario: ツール選択条件の互換性
- **WHEN** AIツールとしてCodexのみを選択したプロジェクトでファイル生成を実行する
- **THEN** `.codex/rules/general.md` と共通テンプレートの下書きが `tasks.md` に同梱され、ClaudeおよびCursor専用の下書きは含まれない

#### Scenario: 再生成時の既存ファイル更新
- **WHEN** 同じプロジェクトで同じパッケージ相対パスのファイルが既に存在する状態でファイル生成を再実行する
- **THEN** 対応する既存の生成ファイルが更新され、その出力パスの重複レコードは作成されない

### Requirement: 再生成時に選択外のファイルを削除する

システムは、ファイル生成（再生成を含む）を実行する際、現在の回答から構成される change パッケージの出力パス集合に含まれない `generated_files` 行を削除しなければならない（MUST）。削除は編集済みフラグの値に関わらず行う。

#### Scenario: 旧構成の残留ファイル削除
- **WHEN** 以前の生成で保存された、現在のパッケージ構成に含まれない出力パスの行が `generated_files` に残っている状態で再生成する
- **THEN** その行は削除され、生成結果は現在の change パッケージ構成と一致する

#### Scenario: ツール選択解除の下書きへの反映
- **WHEN** Claude・Cursor を選択して生成済みのプロジェクトで、`ai_tools` から Cursor を外して再生成する
- **THEN** `tasks.md` から `.cursor/rules/project.mdc` の下書きが消え、`CLAUDE.md` と共通テンプレートの下書きのみが残る

### Requirement: 手動編集されたファイルを再生成から保護する

システムは、編集済みフラグ（`is_edited`）が真の生成ファイルについて、通常の再生成では内容を上書きしてはならない（MUST NOT）。明示的な上書き指定（`force`）がある場合に限り、テンプレート出力で上書きし編集済みフラグを偽に戻す。

#### Scenario: 編集済みファイルの保護
- **WHEN** ユーザーが change パッケージの `tasks.md` を手動編集した後、通常の再生成を実行する
- **THEN** `tasks.md` の内容は編集後のまま維持され、他の未編集ファイルはテンプレート出力で更新される

#### Scenario: 明示的な上書き再生成
- **WHEN** ユーザーが `force` 指定付きで再生成を実行する
- **THEN** 編集済みファイルを含むすべての対象ファイルがテンプレート出力で上書きされ、編集済みフラグは偽に戻る

### Requirement: verify.sh は質問票の全テストツールに対応する

システムは、`test_strategy` の選択肢として提示するすべてのテストツール（pytest・jest・playwright）について、選択時に実行可能なコマンドを `scripts/verify.sh` の下書きに出力しなければならない（MUST）。当該下書きは change パッケージの `tasks.md` に同梱される。

#### Scenario: playwright 選択時のコマンド出力
- **WHEN** `test_strategy` に playwright を含むプロジェクトでファイル生成を実行する
- **THEN** `tasks.md` に同梱される `scripts/verify.sh` の下書きに playwright のテスト実行コマンドが含まれ、「Skipping unsupported test tool」は出力されない
