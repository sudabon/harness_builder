import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

import { projectNamePlaceholder } from "./questionnaire-schema";
import type { PresetStepProps } from "./types";

export function PresetStep({
  applyPreset,
  presets,
  projectName,
  selectedPresetId,
  setProjectName,
}: PresetStepProps) {
  return (
    <div className="space-y-6">
      <label className="block space-y-2">
        <span className="text-sm font-medium">プロジェクト名</span>
        <Input
          onChange={(event) => setProjectName(event.target.value)}
          placeholder={projectNamePlaceholder}
          value={projectName}
        />
      </label>

      <div className="grid gap-3 md:grid-cols-2">
        <button
          className={cn(
            "rounded-3xl border p-4 text-left transition",
            selectedPresetId === null
              ? "border-primary bg-primary/8"
              : "border-border bg-muted/40 hover:bg-card",
          )}
          onClick={() => applyPreset(null)}
          type="button"
        >
          <p className="font-medium">カスタム</p>
          <p className="mt-2 text-sm text-muted-foreground">
            すべての項目を自分で決める構成です。
          </p>
        </button>

        {presets.map((preset) => (
          <button
            className={cn(
              "rounded-3xl border p-4 text-left transition",
              selectedPresetId === preset.id
                ? "border-primary bg-primary/8"
                : "border-border bg-muted/40 hover:bg-card",
            )}
            key={preset.id}
            onClick={() => applyPreset(preset)}
            type="button"
          >
            <p className="font-medium">{preset.name}</p>
            <p className="mt-2 text-sm text-muted-foreground">{preset.description}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
