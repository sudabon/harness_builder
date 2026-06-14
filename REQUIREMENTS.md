# Harness Builder - MVP要求仕様書

## 1. 概要

本サービスは、AIエージェントを活用したソフトウェア開発において必要となる「ハーネス（ルール・テンプレート・評価基盤）」を、
ユーザーの入力に基づいて自動生成するWebアプリケーションである。

ユーザーは簡単な質問に回答するだけで、AIコーディングツール（Claude Code / Codex / Cursor 等）に適したハーネス下書きを含む OpenSpec change パッケージを生成し、対象リポジトリで `/opsx:apply` できる。

---

## 2. ターゲットユーザー

- AIコーディングツールを利用する個人開発者
- 小規模開発チーム（2〜10名）
- AI駆動開発の品質を安定させたいテックリード

---

## 3. 提供価値

- AI開発に必要なハーネスファイルを自動生成
- チームのルール・運用を明文化
- AIの誤動作・事故を未然に防止
- ツール横断で一貫したルールを提供

---

## 4. 機能要件

### 4.1 プロジェクト作成ウィザード

ユーザーは以下の情報を入力する：

#### 必須項目
- プロジェクト種別（Web / API / OSS / SaaS）
- 使用言語（Python / TypeScript 等）
- フレームワーク（FastAPI / React / Next.js 等）
- 使用AIツール（Claude / Codex / Cursor）
- テスト手法（pytest / jest 等）
- Lint / Format（ruff / eslint / prettier 等）
- 禁止事項（例：rm -rf禁止、DB変更禁止など）
- レビュー方針（厳格 / 柔軟）

#### 任意項目
- ブランチ戦略
- CIコマンド
- デプロイ制約
- セキュリティ要件
- 過去の失敗事例
- 命名規約

---

### 4.2 ファイル生成機能

入力内容に基づき、OpenSpec change パッケージ（`openspec/changes/setup-ai-harness/`）を生成する。従来のハーネスファイルは最終ファイルとして直接出力せず、`tasks.md` 内の参照下書きとして同梱する：

#### A. エージェントルール
- AGENTS.md
- PROJECT_RULES.md

#### B. ツール別設定
- CLAUDE.md
- .codex/rules/general.md
- .cursor/rules/project.mdc

#### C. 作業テンプレ
- prompts/feature.md
- prompts/bugfix.md
- prompts/review.md

#### D. 品質管理
- definition_of_done.md
- review_checklist.md
- test_strategy.md

#### E. 実行補助
- scripts/verify.sh

---

### 4.3 プレビュー・編集機能

- 生成された各ファイルをブラウザ上で表示
- 簡易編集機能（テキスト編集）

---

### 4.4 エクスポート機能

- ZIP形式で一括ダウンロード
- ZIPを対象リポジトリのルートに展開すると `openspec/changes/setup-ai-harness/` が配置される
- 対象リポジトリで `/opsx:apply setup-ai-harness` を実行してハーネスを作成する
- ファイル単位でコピー可能

---

### 4.5 プリセット機能

以下のプリセットを選択可能：

- FastAPI + React
- Next.js
- Python API
- SaaS Web App

---

## 5. 非機能要件

- 高速レスポンス（3秒以内）
- モバイル非対応（MVPではPCのみ）
- 多言語対応なし（日本語のみ）

---

## 6. 技術構成

### フロントエンド
- React
- TypeScript
- Tailwind CSS
- Shadcn UI

### バックエンド
- FastAPI
- Jinja2（テンプレート生成）

### データベース
- PostgreSQL

### インフラ
- AWS（ECS Fargate / RDS / S3）

---

## 7. データモデル（簡易）

- users
- projects
- questionnaire_answers
- generated_files

---

## 8. 将来拡張（MVP対象外）

- GitHub連携（直接Push）
- リポジトリ診断
- チーム共有機能
- テンプレートバージョン管理
- 失敗パターン学習
- SSO対応

---

## 9. 成功指標（KPI）

- 生成完了率（ウィザード完走率）
- ZIPダウンロード率
- 再訪率
- 有料転換率（将来）

---

## 10. MVPスコープまとめ

- ウィザード入力
- テンプレ生成
- プレビュー
- ZIPダウンロード
- プリセット

→ 「最短で価値を届ける」ことを優先し、機能を絞る
