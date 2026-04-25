import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

import { optionalStepFields } from "./constants";
import type { AnswerStepProps } from "./types";

export function OptionalItemsStep({ answers, setValue }: AnswerStepProps) {
  return (
    <div className="grid gap-4">
      {optionalStepFields.map((field) => (
        <label className="block space-y-2" key={field.key}>
          <span className="text-sm font-medium">{field.label}</span>
          {field.inputType === "textarea" ? (
            <Textarea
              onChange={(event) => setValue(field.key, event.target.value)}
              value={(answers[field.key] as string) ?? ""}
            />
          ) : (
            <Input
              onChange={(event) => setValue(field.key, event.target.value)}
              value={(answers[field.key] as string) ?? ""}
            />
          )}
        </label>
      ))}
    </div>
  );
}
