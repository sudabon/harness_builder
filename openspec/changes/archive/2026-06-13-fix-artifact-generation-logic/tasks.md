# Tasks: fix-artifact-generation-logic

## 1. DBマイグレーション（バックエンド）

- [x] 1.1 `app/db/models.py` の `GeneratedFile` に `is_edited`（BOOLEAN, NOT NULL, DEFAULT FALSE）を追加
- [x] 1.2 Alembicマイグレーションを作成し、upgrade/downgrade を `tests/test_migrations.py` 相当の手順で検証

## 2. 回答バリデーション（バックエンド）

- [x] 2.1 `app/core/questionnaire.py` に `validate_answers_payload`（既知キーのみ `validate_known_answer_value` を適用、未知キーは素通し）を追加し、ユニットテストを書く
- [x] 2.2 `app/api/routes/projects.py` の `update_answers` で検証を実行し、エラー時はHTTP 400（detailにキー別エラー一覧）を返す。保存はエラーなし時のみ行う
- [x] 2.3 `tests/test_projects.py` に不正選択肢・型不一致・正当値・未知キーの4ケースを追加

## 3. 孤児ファイル削除（バックエンド）

- [x] 3.1 `app/services/generator.py` の `generate_project_files` で、選択されたテンプレートの出力パス集合に含まれない `generated_files` 行を削除する
- [x] 3.2 `tests/test_generation.py` に「ツール選択解除で該当ファイルが消える」「定義外パスの残留行が消える」テストを追加（ファイル一覧・ZIPエクスポート双方で確認）

## 4. 手動編集保護（バックエンド）

- [x] 4.1 `update_file`（PUT /files/{id}）で content 更新時に `is_edited = True` を設定し、レスポンススキーマ（`GeneratedFileResponse` / `GeneratedFileSummaryResponse`）に `is_edited` を追加
- [x] 4.2 `POST /generate` にリクエストボディ `{"force": bool = false}` を追加し、`generate_project_files` で `is_edited=True` の行は force 時のみ上書き（上書き時はフラグをFalseに戻す）するよう変更
- [x] 4.3 `tests/test_generation.py` に「編集済みファイルが通常再生成で保護される」「force で上書きされフラグが戻る」「孤児削除は編集済みでも実行される」テストを追加

## 5. verify.sh の playwright 対応（バックエンド）

- [x] 5.1 `app/templates/scripts/verify.sh.j2` に playwright 分岐（`pnpm exec playwright test`）を追加
- [x] 5.2 `tests/test_generation.py` で playwright 選択時の verify.sh 内容（コマンド出現・Skipping非出現）を検証

## 6. フロントエンド対応

- [x] 6.1 `src/lib/types.ts` と `src/lib/api.ts` に `is_edited` と `generateFiles(id, force?)` を反映
- [x] 6.2 `project-detail-page.tsx` / `file-tree.tsx` に編集済みバッジを表示
- [x] 6.3 再生成ボタンに、編集済みファイル存在時の確認ダイアログ（保護のまま再生成 / force 上書き）を実装。編集済みなしの場合は確認なしで実行
- [x] 6.4 `file-editor.tsx` の保存フローで `is_edited` 反映後の表示を確認し、関連ユニットテストを追加

## 7. 検証

- [x] 7.1 バックエンド全テスト（pytest）とフロントエンドテスト（vitest）を実行しグリーンを確認
- [x] 7.2 docker-compose 環境でウィザード→生成→編集→再生成→ツール選択変更→再生成→ZIPエクスポートの一連を手動確認
