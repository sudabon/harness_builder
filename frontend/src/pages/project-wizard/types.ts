import type { AnswerMap, Preset } from "@/lib/types";

import type { QuestionnaireAnswerKey } from "./questionnaire-schema";

export type AnswerKey = QuestionnaireAnswerKey;

export interface AnswerStepProps {
  answers: AnswerMap;
  setValue: (key: AnswerKey, value: string) => void;
}

export interface PresetStepProps {
  applyPreset: (preset: Preset | null) => void;
  presets: Preset[];
  projectName: string;
  selectedPresetId: string | null;
  setProjectName: (value: string) => void;
}
