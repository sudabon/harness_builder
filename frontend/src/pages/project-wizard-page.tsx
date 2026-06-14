import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ChevronLeft, ChevronRight } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import type { AnswerMap, Preset } from "@/lib/types";
import { ConfirmationStep } from "@/pages/project-wizard/confirmation-step";
import { initialAnswers, steps } from "@/pages/project-wizard/constants";
import { toggleAnswerArrayValue, validateWizardStep } from "@/pages/project-wizard/helpers";
import { OptionalItemsStep } from "@/pages/project-wizard/optional-items-step";
import { PresetStep } from "@/pages/project-wizard/preset-step";
import { RequiredItemsStep } from "@/pages/project-wizard/required-items-step";
import type { AnswerKey } from "@/pages/project-wizard/types";
import { WizardProgressCard } from "@/pages/project-wizard/wizard-progress-card";

export function ProjectWizardPage() {
  const [presets, setPresets] = useState<Preset[]>([]);
  const [projectName, setProjectName] = useState("Harness Builder Demo");
  const [selectedPresetId, setSelectedPresetId] = useState<string | null>(null);
  const [answers, setAnswers] = useState<AnswerMap>(initialAnswers);
  const [projectId, setProjectId] = useState<string | null>(null);
  const [step, setStep] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const navigate = useNavigate();

  useEffect(() => {
    api
      .listPresets()
      .then(setPresets)
      .catch((loadError) => {
        setError(loadError instanceof Error ? loadError.message : "プリセット取得に失敗しました。");
      });
  }, []);

  const toggleArrayValue = useCallback((key: AnswerKey, value: string) => {
    setAnswers((currentAnswers) => toggleAnswerArrayValue(currentAnswers, key, value));
  }, []);

  const setValue = useCallback((key: AnswerKey, value: string) => {
    setAnswers((currentAnswers) => ({ ...currentAnswers, [key]: value }));
  }, []);

  const applyPreset = useCallback((preset: Preset | null) => {
    setSelectedPresetId(preset?.id ?? null);
    setAnswers((currentAnswers) => ({
      ...currentAnswers,
      ...initialAnswers,
      ...(preset?.answers ?? {}),
    }));
  }, []);

  async function ensureProject() {
    if (projectId) {
      return projectId;
    }

    const project = await api.createProject({
      name: projectName,
      preset_id: selectedPresetId,
    });
    setProjectId(project.id);
    return project.id;
  }

  async function goNext() {
    const validationError = validateWizardStep(step, projectName, answers);
    if (validationError) {
      setError(validationError);
      return;
    }

    setError(null);
    if (step === 0) {
      setIsSubmitting(true);
      try {
        await ensureProject();
        setStep((currentStep) => currentStep + 1);
      } catch (submitError) {
        setError(submitError instanceof Error ? submitError.message : "プロジェクト作成に失敗しました。");
      } finally {
        setIsSubmitting(false);
      }
      return;
    }

    setStep((currentStep) => Math.min(currentStep + 1, steps.length - 1));
  }

  async function generate() {
    setError(null);
    setIsSubmitting(true);

    try {
      const ensuredProjectId = await ensureProject();
      await api.updateAnswers(ensuredProjectId, answers);
      await api.generateFiles(ensuredProjectId);
      navigate(`/projects/${ensuredProjectId}`);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "change 生成に失敗しました。");
    } finally {
      setIsSubmitting(false);
    }
  }

  function renderStepContent() {
    if (step === 0) {
      return (
        <PresetStep
          applyPreset={applyPreset}
          presets={presets}
          projectName={projectName}
          selectedPresetId={selectedPresetId}
          setProjectName={setProjectName}
        />
      );
    }

    if (step === 1) {
      return (
        <RequiredItemsStep
          answers={answers}
          setValue={setValue}
          toggleArrayValue={toggleArrayValue}
        />
      );
    }

    if (step === 2) {
      return <OptionalItemsStep answers={answers} setValue={setValue} />;
    }

    if (step === 3) {
      return (
        <ConfirmationStep
          answers={answers}
          presets={presets}
          projectName={projectName}
          selectedPresetId={selectedPresetId}
        />
      );
    }

    return null;
  }

  return (
    <div className="shell grid gap-6 lg:grid-cols-[280px_1fr]">
      <WizardProgressCard step={step} />

      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            <Badge>Step {step + 1}</Badge>
            <p className="section-label">{steps[step].title}</p>
          </div>
          <CardTitle>{steps[step].description}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {renderStepContent()}

          {error ? <p className="text-sm text-danger">{error}</p> : null}

          <div className="flex flex-wrap justify-between gap-3">
            <Button
              disabled={step === 0 || isSubmitting}
              onClick={() => setStep((currentStep) => Math.max(currentStep - 1, 0))}
              type="button"
              variant="outline"
            >
              <ChevronLeft className="h-4 w-4" />
              戻る
            </Button>

            {step < steps.length - 1 ? (
              <Button disabled={isSubmitting} onClick={() => void goNext()} type="button">
                {isSubmitting ? "処理中..." : "次へ"}
                <ChevronRight className="h-4 w-4" />
              </Button>
            ) : (
              <Button disabled={isSubmitting} onClick={() => void generate()} type="button">
                {isSubmitting ? "生成中..." : "change 生成を実行"}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
