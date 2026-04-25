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
}

export const questionnaireFields = [
  {
    key: "project_kind",
    label: "プロジェクト種別",
    inputType: "single_choice",
    required: true,
    defaultValue: "",
    options: ["Web", "API", "OSS", "SaaS"],
    step: "required",
  },
  {
    key: "languages",
    label: "languages",
    inputType: "multi_choice",
    required: true,
    defaultValue: [],
    options: ["Python", "TypeScript", "Go", "Rust"],
    step: "required",
  },
  {
    key: "frameworks",
    label: "frameworks",
    inputType: "multi_choice",
    required: true,
    defaultValue: [],
    options: ["FastAPI", "React", "Next.js", "Django"],
    step: "required",
  },
  {
    key: "ai_tools",
    label: "ai_tools",
    inputType: "multi_choice",
    required: true,
    defaultValue: [],
    options: ["Claude", "Codex", "Cursor"],
    step: "required",
  },
  {
    key: "test_strategy",
    label: "test_strategy",
    inputType: "multi_choice",
    required: true,
    defaultValue: [],
    options: ["pytest", "jest", "playwright"],
    step: "required",
  },
  {
    key: "lint_format",
    label: "lint_format",
    inputType: "multi_choice",
    required: true,
    defaultValue: [],
    options: ["ruff", "eslint", "prettier"],
    step: "required",
  },
  {
    key: "prohibited_actions",
    label: "禁止事項",
    inputType: "textarea",
    required: true,
    defaultValue: "",
    options: [],
    step: "required",
  },
  {
    key: "review_policy",
    label: "レビュー方針",
    inputType: "single_choice",
    required: true,
    defaultValue: "",
    options: ["厳格", "柔軟"],
    step: "required",
  },
  {
    key: "branch_strategy",
    label: "ブランチ戦略",
    inputType: "text",
    required: false,
    defaultValue: "",
    options: [],
    step: "optional",
  },
  {
    key: "ci_command",
    label: "CI コマンド",
    inputType: "text",
    required: false,
    defaultValue: "",
    options: [],
    step: "optional",
  },
  {
    key: "deploy_constraints",
    label: "デプロイ制約",
    inputType: "textarea",
    required: false,
    defaultValue: "",
    options: [],
    step: "optional",
  },
  {
    key: "security_requirements",
    label: "セキュリティ要件",
    inputType: "textarea",
    required: false,
    defaultValue: "",
    options: [],
    step: "optional",
  },
  {
    key: "failure_examples",
    label: "過去の失敗事例",
    inputType: "textarea",
    required: false,
    defaultValue: "",
    options: [],
    step: "optional",
  },
  {
    key: "naming_convention",
    label: "命名規約",
    inputType: "text",
    required: false,
    defaultValue: "",
    options: [],
    step: "optional",
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
