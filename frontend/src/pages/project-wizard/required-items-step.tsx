import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

import {
  prohibitedActionsField,
  projectKindField,
  requiredMultiChoiceFields,
  reviewPolicyField,
} from "./constants";
import type { AnswerStepProps, AnswerKey } from "./types";

interface RequiredItemsStepProps extends AnswerStepProps {
  toggleArrayValue: (key: AnswerKey, value: string) => void;
}

export function RequiredItemsStep({
  answers,
  setValue,
  toggleArrayValue,
}: RequiredItemsStepProps) {
  return (
    <div className="space-y-6">
      <div className="space-y-3">
        <span className="text-sm font-medium">{projectKindField.label}</span>
        <div className="flex flex-wrap gap-2">
          {projectKindField.options?.map((option) => (
            <Button
              key={option}
              onClick={() => setValue(projectKindField.key, option)}
              type="button"
              variant={answers[projectKindField.key] === option ? "primary" : "outline"}
            >
              {option}
            </Button>
          ))}
        </div>
      </div>

      {requiredMultiChoiceFields.map((field) => (
        <div className="space-y-3" key={field.key}>
          <span className="text-sm font-medium">{field.label}</span>
          <div className="flex flex-wrap gap-2">
            {field.options?.map((option) => {
              const selected =
                Array.isArray(answers[field.key]) && answers[field.key].includes(option);
              return (
                <Button
                  key={option}
                  onClick={() => toggleArrayValue(field.key, option)}
                  type="button"
                  variant={selected ? "secondary" : "outline"}
                >
                  {option}
                </Button>
              );
            })}
          </div>
        </div>
      ))}

      <label className="block space-y-2">
        <span className="text-sm font-medium">{prohibitedActionsField.label}</span>
        <Textarea
          onChange={(event) => setValue(prohibitedActionsField.key, event.target.value)}
          value={(answers[prohibitedActionsField.key] as string) ?? ""}
        />
      </label>

      <div className="space-y-3">
        <span className="text-sm font-medium">{reviewPolicyField.label}</span>
        <div className="flex flex-wrap gap-2">
          {reviewPolicyField.options?.map((option) => (
            <Button
              key={option}
              onClick={() => setValue(reviewPolicyField.key, option)}
              type="button"
              variant={answers[reviewPolicyField.key] === option ? "primary" : "outline"}
            >
              {option}
            </Button>
          ))}
        </div>
      </div>
    </div>
  );
}
