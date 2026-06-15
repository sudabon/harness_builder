import type { AnswerMap, AnswerValue } from "@/lib/types";

export type QuestionnaireInputType = "single_choice" | "multi_choice" | "text" | "textarea";
export type WizardStepId = "required" | "optional";

export interface QuestionnaireField {
  key: string;
  label: string;
  inputType: QuestionnaireInputType;
  required: boolean;
  defaultValue: AnswerValue;
  options?: readonly string[];
  step?: WizardStepId;
  /** テキスト入力の placeholder、または選択式フィールドの入力例ヒント */
  placeholder?: string;
}

export const projectNamePlaceholder = "例: Harness Builder Demo";

export const projectKindProfiles = [
  {
    value: "Web",
    title: "Webアプリ",
    description: "ブラウザで使う画面体験が主役のリポジトリ。",
    generatedFocus: "UI状態、アクセシビリティ、E2E、画面回帰を重視",
  },
  {
    value: "API",
    title: "APIサービス",
    description: "外部または内部システムへ機能を提供するサービス。",
    generatedFocus: "API契約、認証、エラー設計、互換性、負荷を重視",
  },
  {
    value: "OSS",
    title: "OSS / ライブラリ",
    description: "公開・再利用・配布されるパッケージやCLI。",
    generatedFocus: "README、SemVer、破壊的変更、リリース手順を重視",
  },
  {
    value: "SaaS",
    title: "SaaSプロダクト",
    description: "顧客向けに継続運用するプロダクト。",
    generatedFocus: "テナント分離、課金、監査ログ、SLO、セキュリティを重視",
  },
] as const;

export function getProjectKindProfile(value: AnswerValue) {
  const normalized = Array.isArray(value) ? value[0] : value;
  return projectKindProfiles.find((profile) => profile.value === normalized);
}

export const questionnaireFields = [
  {
    key: "project_kind",
    label: "成果物タイプ",
    inputType: "single_choice",
    required: true,
    defaultValue: "",
    options: ["Web", "API", "OSS", "SaaS"],
    step: "required",
    placeholder: "例: 画面が中心なら Web、REST/gRPC サービスなら API、公開ライブラリなら OSS",
  },
  {
    key: "languages",
    label: "使用言語",
    inputType: "multi_choice",
    required: true,
    defaultValue: [],
    options: ["Python", "TypeScript", "Go", "Rust"],
    step: "required",
    placeholder: "例: Python と TypeScript を選択（フルスタック構成）",
  },
  {
    key: "frameworks",
    label: "フレームワーク",
    inputType: "multi_choice",
    required: true,
    defaultValue: [],
    options: ["FastAPI", "React", "Next.js", "Django", "Echo", "Buf"],
    step: "required",
    placeholder: "例: FastAPI + React、または Next.js のみ",
  },
  {
    key: "ai_tools",
    label: "AI ツール",
    inputType: "multi_choice",
    required: true,
    defaultValue: [],
    options: ["Claude", "Codex", "Cursor"],
    step: "required",
    placeholder: "例: チームで使うツールをすべて選択（Claude / Codex / Cursor）",
  },
  {
    key: "test_strategy",
    label: "テスト手法",
    inputType: "multi_choice",
    required: true,
    defaultValue: [],
    options: ["pytest", "vitest", "testing", "jest", "playwright"],
    step: "required",
    placeholder: "例: pytest（バックエンド）+ vitest（フロント）+ playwright（E2E）",
  },
  {
    key: "lint_format",
    label: "Lint / フォーマット",
    inputType: "multi_choice",
    required: true,
    defaultValue: [],
    options: ["ruff", "mypy", "eslint", "prettier", "gofmt", "golangci-lint"],
    step: "required",
    placeholder: "例: ruff + mypy（Python）、eslint + prettier（TypeScript）",
  },
  {
    key: "prohibited_actions",
    label: "禁止事項",
    inputType: "textarea",
    required: true,
    defaultValue: "",
    options: [],
    step: "required",
    placeholder:
      "例: 本番DBへの直接変更禁止、main への force push 禁止、秘密情報のコミット禁止、未レビューのマージ禁止",
  },
  {
    key: "review_policy",
    label: "レビュー方針",
    inputType: "single_choice",
    required: true,
    defaultValue: "",
    options: ["厳格", "柔軟"],
    step: "required",
    placeholder: "例: 本番影響がある変更は厳格、ドキュメント修正のみなら柔軟",
  },
  {
    key: "branch_strategy",
    label: "ブランチ戦略",
    inputType: "text",
    required: false,
    defaultValue: "",
    options: [],
    step: "optional",
    placeholder: "例: main から feature ブランチを切り、PR マージ後に削除。hotfix は release ブランチ経由",
  },
  {
    key: "ci_command",
    label: "CI コマンド",
    inputType: "text",
    required: false,
    defaultValue: "",
    options: [],
    step: "optional",
    placeholder: "例: pnpm lint && pnpm test && uv run pytest",
  },
  {
    key: "deploy_constraints",
    label: "デプロイ制約",
    inputType: "textarea",
    required: false,
    defaultValue: "",
    options: [],
    step: "optional",
    placeholder:
      "例: 平日 10:00–17:00 のみ本番デプロイ可。金曜午後のリリース禁止。メンテナンス前日はデプロイしない",
  },
  {
    key: "security_requirements",
    label: "セキュリティ要件",
    inputType: "textarea",
    required: false,
    defaultValue: "",
    options: [],
    step: "optional",
    placeholder:
      "例: API キー・DB 接続情報は .env で管理しコードにハードコードしない。依存関係は月1回監査する",
  },
  {
    key: "failure_examples",
    label: "過去の失敗事例",
    inputType: "textarea",
    required: false,
    defaultValue: "",
    options: [],
    step: "optional",
    placeholder:
      "例: レビューなしで main に直接 push し本番障害が発生した。テスト未追加でリグレッションを見逃した",
  },
  {
    key: "naming_convention",
    label: "命名規約",
    inputType: "text",
    required: false,
    defaultValue: "",
    options: [],
    step: "optional",
    placeholder:
      "例: ファイル・ディレクトリは kebab-case、Python は snake_case、React コンポーネントは PascalCase",
  },
] as const satisfies readonly QuestionnaireField[];

export type QuestionnaireAnswerKey = (typeof questionnaireFields)[number]["key"];

export const questionnaireFieldsByKey = Object.fromEntries(
  questionnaireFields.map((field) => [field.key, field]),
) as Record<QuestionnaireAnswerKey, (typeof questionnaireFields)[number]>;

export function createInitialAnswers(): AnswerMap {
  return Object.fromEntries(
    questionnaireFields.map((field) => [
      field.key,
      Array.isArray(field.defaultValue) ? [...field.defaultValue] : field.defaultValue,
    ]),
  );
}

export function getFieldsForStep(step: WizardStepId) {
  return questionnaireFields.filter((field) => field.step === step);
}

export function getRequiredAnswerKeys() {
  return questionnaireFields.filter((field) => field.required).map((field) => field.key);
}
