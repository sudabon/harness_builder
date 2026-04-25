## Context

Harness Builder のバックエンドはFastAPI、SQLAlchemy、Alembicを使い、開発時の既定DBはSQLite、docker-compose環境ではPostgreSQLを使う。現在は `backend/alembic/versions/20260418_0001_initial.py` が初期スキーマを作成し、モデル側には `users`, `projects`, `questionnaire_answers`, `generated_files` が定義されている。

一方、テストでは `Base.metadata.create_all()` によりスキーマを直接作成しているため、Alembicマイグレーションが実際に最新モデルと一致しているかをテストで検知しにくい。この変更では、既存スキーマを変更せずにAlembicを正規のスキーマ適用経路として統一する。

## Goals / Non-Goals

**Goals:**

- Alembic revision graph を単一の `head` として維持する
- クリーンなDBに `alembic upgrade head` を適用すると、既存モデルと同等のスキーマが作成される状態にする
- 既存のテーブル、カラム、外部キー、ユニーク制約、インデックス名を維持する
- テストでマイグレーション適用結果を検証できるようにする
- SQLiteテスト環境とPostgreSQL開発環境の両方で実行できる検証手順を整える

**Non-Goals:**

- テーブル・カラム・制約の追加、削除、名称変更
- 既存データの移行や破壊的な再作成
- API、サービス、フロントエンドの挙動変更
- Alembic以外のマイグレーションツール導入

## Decisions

1. Alembicを唯一の正式なスキーマ適用経路として扱う。
   - 理由: 本番に近い適用経路をテストでも確認することで、モデルとマイグレーションの乖離を早期に検知できる。
   - 代替案: テストでは `Base.metadata.create_all()` を使い続ける。高速だが、マイグレーションの破損を検知できない。

2. 既存の初期マイグレーションを現在モデルに合わせて整えるが、スキーマ内容は変えない。
   - 理由: MVPはまだ初期段階であり、既存の正式な履歴は1本だけなので、履歴を増やすより単一の正しい初期スキーマを維持する方が分かりやすい。
   - 代替案: 差分修正用の追加revisionを作る。既存スキーマ差分がない場合は履歴だけが増え、保守性が下がる。

3. テスト用DBの作成もAlembic経由へ寄せる。
   - 理由: APIテストが利用するスキーマとマイグレーション後スキーマを一致させられる。
   - 代替案: マイグレーション専用テストだけを追加し、既存fixtureは `create_all()` のままにする。移行リスクは低いが、通常テストが別経路のスキーマで動き続ける。

4. SQLiteとPostgreSQLの差異は既存型・制約の範囲で扱い、新しいDB固有機能は使わない。
   - 理由: テスト容易性とMVPのポータビリティを維持するため。
   - 代替案: PostgreSQL固有型や制約に寄せる。将来的には選択肢だが、現時点ではローカルテストの複雑度が上がる。

## Risks / Trade-offs

- [テスト実行時間の増加] → Alembic適用は初期スキーマのみなので影響は小さい。必要ならfixture単位でエンジン再利用を検討する
- [SQLiteとPostgreSQLのDDL差異] → 既存のString/Text/DateTime/ForeignKey/UniqueConstraint/Indexの範囲に留める
- [既存ローカルSQLiteファイルの状態差異] → `alembic upgrade head` と `alembic current` で状態確認できる手順を明示する
- [履歴の書き換えに見える変更] → 既存スキーマが正式運用前の初期revisionであることを前提に、データ破壊を伴わない範囲に限定する

## Migration Plan

1. 現在のSQLAlchemyモデルと初期Alembic revisionのテーブル、カラム、制約、インデックスを照合する。
2. Alembic設定が `DATABASE_URL` を通じてSQLite/PostgreSQLどちらにも適用できることを確認する。
3. テストfixtureまたは専用テストをAlembic適用経路へ寄せる。
4. クリーンDBで `alembic upgrade head`、`alembic current`、バックエンドテストを実行する。

ロールバックが必要な場合は、テストfixtureと検証テストの変更を戻す。既存スキーマ内容は変更しないため、保存済みデータの復旧作業は不要。

## Open Questions

なし
