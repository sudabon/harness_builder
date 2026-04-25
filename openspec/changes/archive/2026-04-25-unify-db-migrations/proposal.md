## Why

データベーススキーマはSQLAlchemyモデルとAlembicマイグレーションの両方で表現されているが、現状はテストが `Base.metadata.create_all()` に依存しており、マイグレーションの正しさを継続的に確認できていない。MVPのデータ互換性を守るため、Alembicを唯一の適用経路として扱える状態に整理する。

## What Changes

- Alembicマイグレーションを、現在のSQLAlchemyモデルと一致する正式なスキーマ定義として整理する
- ローカル開発・テスト・PostgreSQL環境で同じマイグレーション履歴を使えることを検証できるようにする
- テスト環境がモデル直作成ではなくマイグレーション適用結果を確認できるようにする
- 既存テーブル、カラム、制約、インデックス、API挙動は変更しない

## Capabilities

### New Capabilities

- `database-migrations`: Alembicによるデータベーススキーマ管理、アップグレード検証、モデルとの整合性確認

### Modified Capabilities

なし

## Impact

- 影響範囲: `backend/alembic/`, `backend/alembic.ini`, `backend/tests/conftest.py`, マイグレーション検証用テスト
- API互換性: 既存APIエンドポイントとレスポンス形式は変更しない
- データ互換性: 既存テーブル名、カラム名、制約名、インデックス名は維持する
- 依存関係: 既存のAlembic / SQLAlchemyを利用し、新規外部依存は追加しない
