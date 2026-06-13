# Capability: file-generation

## Purpose

Harness Builder のウィザード回答から、テンプレートベースでハーネス関連ファイルを生成し、プロジェクト単位で保存できるようにする。
## Requirements
### Requirement: ウィザード回答からハーネスファイルを生成する

システムはウィザードの回答内容に基づき、Jinja2テンプレートエンジンを使用してハーネスファイル群を生成する。生成はAPIリクエストにより実行される。

#### Scenario: ファイル生成の実行
- **WHEN** ユーザーがウィザード完了後に「生成」ボタンを押す
- **THEN** `POST /api/v1/projects/{id}/generate` が呼ばれ、回答に基づくファイル群がgenerated_filesテーブルに保存される

#### Scenario: 生成完了の応答
- **WHEN** ファイル生成が正常に完了する
- **THEN** 3秒以内にレスポンスが返り、生成されたファイル一覧が含まれる

### Requirement: エージェントルールファイルを生成する

システムは以下のエージェントルールファイルを生成する：
- `AGENTS.md` — エージェントの役割・権限・行動規範
- `PROJECT_RULES.md` — プロジェクト全体のルール定義

#### Scenario: エージェントルール生成
- **WHEN** プロジェクト種別・禁止事項・レビュー方針が入力されている
- **THEN** 入力内容を反映した `AGENTS.md` と `PROJECT_RULES.md` が生成される

### Requirement: ツール別設定ファイルを生成する

選択されたAIツールに応じて、対応する設定ファイルを生成する：
- Claude選択時: `CLAUDE.md`
- Codex選択時: `.codex/rules/general.md`
- Cursor選択時: `.cursor/rules/project.mdc`

#### Scenario: Claudeのみ選択
- **WHEN** ユーザーがAIツールとしてClaudeのみを選択する
- **THEN** `CLAUDE.md` のみが生成され、他ツールの設定ファイルは生成されない

#### Scenario: 複数ツール選択
- **WHEN** ユーザーがClaude・Codex・Cursorすべてを選択する
- **THEN** `CLAUDE.md`、`.codex/rules/general.md`、`.cursor/rules/project.mdc` がすべて生成される

### Requirement: 作業テンプレートファイルを生成する

システムは以下のプロンプトテンプレートを生成する：
- `prompts/feature.md` — 機能追加用プロンプト
- `prompts/bugfix.md` — バグ修正用プロンプト
- `prompts/review.md` — コードレビュー用プロンプト

#### Scenario: 作業テンプレート生成
- **WHEN** ファイル生成が実行される
- **THEN** プロジェクトの言語・FW・テスト手法を反映した3つのテンプレートが生成される

### Requirement: 品質管理ファイルを生成する

システムは以下の品質管理ファイルを生成する：
- `definition_of_done.md` — 完了定義
- `review_checklist.md` — レビューチェックリスト
- `test_strategy.md` — テスト戦略

#### Scenario: 品質管理ファイル生成
- **WHEN** テスト手法・Lint設定・レビュー方針が入力されている
- **THEN** 入力内容を反映した品質管理ファイル群が生成される

### Requirement: 実行補助スクリプトを生成する

システムは `scripts/verify.sh` を生成する。このスクリプトはLint・テスト・ビルドの一括実行を行う。

#### Scenario: verify.sh生成
- **WHEN** Lint/FormatツールとテストFWが入力されている
- **THEN** 対応するコマンドを含む `scripts/verify.sh` が生成される

### Requirement: 生成サービス整理後も生成互換性を維持する

システムは、サービス層の内部構造を整理しても、ウィザード回答とテンプレート定義から生成されるファイルのパス、内容、ツール選択条件を維持しなければならない（MUST）。

#### Scenario: 既存テンプレート出力の互換性
- **WHEN** 必須回答が揃ったプロジェクトでファイル生成を実行する
- **THEN** 選択されたAIツールと共通テンプレートに対応する生成ファイルが、従来と同じファイルパスで保存される

#### Scenario: ツール選択条件の互換性
- **WHEN** AIツールとしてCodexのみを選択したプロジェクトでファイル生成を実行する
- **THEN** `.codex/rules/general.md` と共通テンプレートのファイルが生成され、ClaudeおよびCursor専用ファイルは生成結果に含まれない

#### Scenario: 再生成時の既存ファイル更新
- **WHEN** 同じプロジェクトで同じ出力パスのファイルが既に存在する状態でファイル生成を再実行する
- **THEN** 対応する既存の生成ファイルが更新され、その出力パスの重複レコードは作成されない

### Requirement: 再生成時に選択外のファイルを削除する

システムは、ファイル生成（再生成を含む）を実行する際、現在の回答から選択されるテンプレート定義の出力パス集合に含まれない `generated_files` 行を削除しなければならない（MUST）。削除は編集済みフラグの値に関わらず行う。

#### Scenario: ツール選択解除による孤児ファイル削除
- **WHEN** Claude・Cursor を選択して生成済みのプロジェクトで、`ai_tools` から Cursor を外して再生成する
- **THEN** `.cursor/rules/project.mdc` がファイル一覧およびZIPエクスポートから消え、`CLAUDE.md` と共通テンプレートのファイルのみが残る

#### Scenario: テンプレート定義に存在しないファイルの削除
- **WHEN** テンプレート定義に存在しない出力パスの行が `generated_files` に残っている状態で再生成する
- **THEN** その行は削除され、生成結果は現在のテンプレート定義と一致する

### Requirement: 手動編集されたファイルを再生成から保護する

システムは、編集済みフラグ（`is_edited`）が真の生成ファイルについて、通常の再生成では内容を上書きしてはならない（MUST NOT）。明示的な上書き指定（`force`）がある場合に限り、テンプレート出力で上書きし編集済みフラグを偽に戻す。

#### Scenario: 編集済みファイルの保護
- **WHEN** ユーザーが `AGENTS.md` を手動編集した後、通常の再生成を実行する
- **THEN** `AGENTS.md` の内容は編集後のまま維持され、他の未編集ファイルはテンプレート出力で更新される

#### Scenario: 明示的な上書き再生成
- **WHEN** ユーザーが `force` 指定付きで再生成を実行する
- **THEN** 編集済みファイルを含むすべての対象ファイルがテンプレート出力で上書きされ、編集済みフラグは偽に戻る

### Requirement: verify.sh は質問票の全テストツールに対応する

システムは、`test_strategy` の選択肢として提示するすべてのテストツール（pytest・jest・playwright）について、選択時に実行可能なコマンドを `scripts/verify.sh` に出力しなければならない（MUST）。

#### Scenario: playwright 選択時のコマンド出力
- **WHEN** `test_strategy` に playwright を含むプロジェクトでファイル生成を実行する
- **THEN** 生成された `scripts/verify.sh` に playwright のテスト実行コマンドが含まれ、「Skipping unsupported test tool」は出力されない

