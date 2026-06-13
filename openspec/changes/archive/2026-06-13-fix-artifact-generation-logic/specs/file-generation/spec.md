# Delta: file-generation

## ADDED Requirements

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
