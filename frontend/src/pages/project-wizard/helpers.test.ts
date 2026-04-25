import { describe, expect, it } from "vitest";

import { initialAnswers } from "./constants";
import { toggleAnswerArrayValue, validateWizardStep } from "./helpers";

describe("project wizard helpers", () => {
  it("toggles array answer values without changing unrelated answers", () => {
    const added = toggleAnswerArrayValue(initialAnswers, "languages", "Python");

    expect(added.languages).toEqual(["Python"]);
    expect(added.project_kind).toBe("");

    const removed = toggleAnswerArrayValue(added, "languages", "Python");

    expect(removed.languages).toEqual([]);
  });

  it("preserves project-name and required-answer validation messages", () => {
    expect(validateWizardStep(0, "  ", initialAnswers)).toBe(
      "プロジェクト名を入力してください。",
    );
    expect(validateWizardStep(1, "Harness Builder Demo", initialAnswers)).toBe(
      "必須項目をすべて入力してください。",
    );

    expect(
      validateWizardStep(1, "Harness Builder Demo", {
        ...initialAnswers,
        project_kind: "Web",
        languages: ["Python"],
        frameworks: ["FastAPI"],
        ai_tools: ["Codex"],
        test_strategy: ["pytest"],
        lint_format: ["ruff"],
        prohibited_actions: "本番DBの直接変更禁止",
        review_policy: "厳格",
      }),
    ).toBeNull();
  });
});
