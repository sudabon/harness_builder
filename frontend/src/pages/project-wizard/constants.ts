import {
  createInitialAnswers,
  getFieldsForStep,
  getRequiredAnswerKeys,
  questionnaireFieldsByKey,
} from "./questionnaire-schema";

export const requiredFields = getRequiredAnswerKeys();
export const initialAnswers = createInitialAnswers();

export const steps = [
  { title: "プリセット", description: "プロジェクト名と初期プリセットを選択" },
  { title: "必須項目", description: "生成に必要な入力を埋める" },
  { title: "任意項目", description: "運用ルールを追加する" },
  { title: "確認", description: "内容を確認してファイル生成を実行" },
];

export const requiredStepFields = getFieldsForStep("required");
export const optionalStepFields = getFieldsForStep("optional");
export const projectKindField = questionnaireFieldsByKey.project_kind;
export const prohibitedActionsField = questionnaireFieldsByKey.prohibited_actions;
export const reviewPolicyField = questionnaireFieldsByKey.review_policy;
export const requiredMultiChoiceFields = requiredStepFields.filter(
  (field) => field.inputType === "multi_choice",
);
