import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

import {
  prohibitedActionsField,
  projectKindField,
  requiredMultiChoiceFields,
  reviewPolicyField,
} from "./constants";
import { FieldHint } from "./field-hint";
import { projectKindProfiles } from "./questionnaire-schema";
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
      <fieldset className="space-y-3">
        <legend className="text-sm font-medium">{projectKindField.label}</legend>
        <FieldHint text={projectKindField.placeholder} />
        <p className="text-sm text-muted-foreground">
          生成するハーネスが最も重視すべきリポジトリの性格を選びます。
        </p>
        <div className="grid gap-3 md:grid-cols-2">
          {projectKindProfiles.map((profile) => {
            const selected = answers[projectKindField.key] === profile.value;

            return (
              <label
                className={cn(
                  "min-h-36 cursor-pointer rounded-lg border p-4 transition-colors",
                  "focus-within:outline focus-within:outline-2 focus-within:outline-offset-2 focus-within:outline-primary/50",
                  selected
                    ? "border-primary bg-primary/8"
                    : "border-border bg-muted/40 hover:bg-card",
                )}
                key={profile.value}
              >
                <input
                  checked={selected}
                  className="sr-only"
                  name={projectKindField.key}
                  onChange={() => setValue(projectKindField.key, profile.value)}
                  type="radio"
                  value={profile.value}
                />
                <span className="flex items-center justify-between gap-3">
                  <span className="font-medium">{profile.title}</span>
                  <span className="rounded-full border border-current px-2 py-0.5 text-xs text-muted-foreground">
                    {profile.value}
                  </span>
                </span>
                <span className="mt-2 block text-sm text-muted-foreground">
                  {profile.description}
                </span>
                <span className="mt-3 block text-xs leading-relaxed text-foreground">
                  生成焦点: {profile.generatedFocus}
                </span>
              </label>
            );
          })}
        </div>
      </fieldset>

      {requiredMultiChoiceFields.map((field) => (
        <div className="space-y-3" key={field.key}>
          <span className="text-sm font-medium">{field.label}</span>
          <FieldHint text={field.placeholder} />
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
          placeholder={prohibitedActionsField.placeholder}
          value={(answers[prohibitedActionsField.key] as string) ?? ""}
        />
      </label>

      <div className="space-y-3">
        <span className="text-sm font-medium">{reviewPolicyField.label}</span>
        <FieldHint text={reviewPolicyField.placeholder} />
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
