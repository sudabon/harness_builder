# Capability: presets

## Purpose

定義済みプリセットを通じて、ウィザード入力の初期値を高速に設定し、ユーザーが共通パターンからすぐに開始できるようにする。

## Requirements

### Requirement: プリセットを選択してウィザードを事前入力できる

ユーザーはプリセットを選択することで、ウィザードの必須項目を一括で事前入力できる。プリセット適用後も各項目を個別に変更可能。

#### Scenario: プリセット一覧の表示
- **WHEN** ユーザーがプロジェクト新規作成を開始する
- **THEN** 利用可能なプリセット（FastAPI + React / Next.js / Python API / SaaS Web App）が選択肢として表示される

#### Scenario: プリセットの適用
- **WHEN** ユーザーが「FastAPI + React」プリセットを選択する
- **THEN** プロジェクト種別=Web、使用言語=Python+TypeScript、フレームワーク=FastAPI+React、テスト=pytest+jest、Lint=ruff+eslint がウィザードに事前入力される

#### Scenario: プリセット適用後の項目変更
- **WHEN** ユーザーがプリセット適用後にウィザードの項目を変更する
- **THEN** 変更した項目のみが更新され、他のプリセット値は保持される

#### Scenario: プリセットなしで開始
- **WHEN** ユーザーがプリセットを選択せずに「カスタム」を選ぶ
- **THEN** すべての項目が空の状態でウィザードが開始される

### Requirement: プリセット定義をAPIから取得する

プリセットの定義はバックエンドAPIで管理され、フロントエンドから取得する。

#### Scenario: プリセット一覧の取得
- **WHEN** フロントエンドがプリセット一覧を要求する
- **THEN** `GET /api/v1/presets` から各プリセットのID・名前・事前入力値を含むJSONが返される
