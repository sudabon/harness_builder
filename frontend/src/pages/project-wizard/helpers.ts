import type { AnswerMap } from "@/lib/types";

import { requiredFields } from "./constants";
import type { AnswerKey } from "./types";

export function toggleAnswerArrayValue(
  answers: AnswerMap,
  key: AnswerKey,
  value: string,
): AnswerMap {
  const current = Array.isArray(answers[key]) ? answers[key] : [];
  return {
    ...answers,
    [key]: current.includes(value)
      ? current.filter((item) => item !== value)
      : [...current, value],
  };
}

export function validateWizardStep(
  step: number,
  projectName: string,
  answers: AnswerMap,
): string | null {
  if (step === 0 && projectName.trim().length === 0) {
    return "プロジェクト名を入力してください。";
  }

  if (step === 1) {
    const missing = requiredFields.filter((key) => {
      const value = answers[key];
      if (Array.isArray(value)) {
        return value.length === 0;
      }
      return !value;
    });
    if (missing.length > 0) {
      return "必須項目をすべて入力してください。";
    }
  }

  return null;
}
