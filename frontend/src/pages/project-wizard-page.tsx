import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Check, ChevronLeft, ChevronRight } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { api } from "@/lib/api";
import type { AnswerMap, Preset } from "@/lib/types";
import { cn } from "@/lib/utils";

const requiredFields = [
  "project_kind",
  "languages",
  "frameworks",
  "ai_tools",
  "test_strategy",
  "lint_format",
  "prohibited_actions",
  "review_policy",
] as const;

const initialAnswers: AnswerMap = {
  project_kind: "",
  languages: [],
  frameworks: [],
  ai_tools: [],
  test_strategy: [],
  lint_format: [],
  prohibited_actions: "",
  review_policy: "",
  branch_strategy: "",
  ci_command: "",
  deploy_constraints: "",
  security_requirements: "",
  failure_examples: "",
  naming_convention: "",
};

const steps = [
  { title: "プリセット", description: "プロジェクト名と初期プリセットを選択" },
  { title: "必須項目", description: "生成に必要な入力を埋める" },
  { title: "任意項目", description: "運用ルールを追加する" },
  { title: "確認", description: "内容を確認してファイル生成を実行" },
];

const checkboxGroups = {
  languages: ["Python", "TypeScript", "Go", "Rust"],
  frameworks: ["FastAPI", "React", "Next.js", "Django"],
  ai_tools: ["Claude", "Codex", "Cursor"],
  test_strategy: ["pytest", "jest", "playwright"],
  lint_format: ["ruff", "eslint", "prettier"],
} satisfies Record<string, string[]>;

const projectKinds = ["Web", "API", "OSS", "SaaS"];
const reviewPolicies = ["厳格", "柔軟"];

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

  function toggleArrayValue(key: keyof AnswerMap, value: string) {
    const current = Array.isArray(answers[key]) ? answers[key] : [];
    setAnswers((currentAnswers) => ({
      ...currentAnswers,
      [key]: current.includes(value)
        ? current.filter((item) => item !== value)
        : [...current, value],
    }));
  }

  function setValue(key: keyof AnswerMap, value: string) {
    setAnswers((currentAnswers) => ({ ...currentAnswers, [key]: value }));
  }

  function applyPreset(preset: Preset | null) {
    setSelectedPresetId(preset?.id ?? null);
    setAnswers((currentAnswers) => ({
      ...currentAnswers,
      ...initialAnswers,
      ...(preset?.answers ?? {}),
    }));
  }

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

  function validateCurrentStep() {
    if (step === 0 && projectName.trim().length === 0) {
      return "プロジェクト名を入力してください。";
    }

    if (step === 1) {
      const missing = requiredFields.filter((field) => {
        const value = answers[field];
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

  async function goNext() {
    const validationError = validateCurrentStep();
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
      setError(submitError instanceof Error ? submitError.message : "ファイル生成に失敗しました。");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="shell grid gap-6 lg:grid-cols-[280px_1fr]">
      <Card>
        <CardHeader>
          <p className="section-label">Wizard Progress</p>
          <CardTitle>プロジェクト作成</CardTitle>
          <CardDescription>4ステップでハーネスを生成します。</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {steps.map((item, index) => (
            <div
              className={cn(
                "rounded-3xl border px-4 py-3",
                index === step ? "border-primary bg-primary/8" : "border-border bg-muted/40",
              )}
              key={item.title}
            >
              <div className="flex items-center gap-3">
                <div
                  className={cn(
                    "flex h-8 w-8 items-center justify-center rounded-full text-sm",
                    index < step
                      ? "bg-primary text-primary-foreground"
                      : index === step
                        ? "bg-accent text-accent-foreground"
                        : "bg-card text-muted-foreground",
                  )}
                >
                  {index < step ? <Check className="h-4 w-4" /> : index + 1}
                </div>
                <div>
                  <p className="font-medium">{item.title}</p>
                  <p className="text-xs text-muted-foreground">{item.description}</p>
                </div>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            <Badge>Step {step + 1}</Badge>
            <p className="section-label">{steps[step].title}</p>
          </div>
          <CardTitle>{steps[step].description}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {step === 0 ? (
            <div className="space-y-6">
              <label className="block space-y-2">
                <span className="text-sm font-medium">プロジェクト名</span>
                <Input onChange={(event) => setProjectName(event.target.value)} value={projectName} />
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
          ) : null}

          {step === 1 ? (
            <div className="space-y-6">
              <div className="space-y-3">
                <span className="text-sm font-medium">プロジェクト種別</span>
                <div className="flex flex-wrap gap-2">
                  {projectKinds.map((option) => (
                    <Button
                      key={option}
                      onClick={() => setValue("project_kind", option)}
                      type="button"
                      variant={answers.project_kind === option ? "primary" : "outline"}
                    >
                      {option}
                    </Button>
                  ))}
                </div>
              </div>

              {Object.entries(checkboxGroups).map(([key, options]) => (
                <div className="space-y-3" key={key}>
                  <span className="text-sm font-medium">{key}</span>
                  <div className="flex flex-wrap gap-2">
                    {options.map((option) => {
                      const selected =
                        Array.isArray(answers[key]) && (answers[key] as string[]).includes(option);
                      return (
                        <Button
                          key={option}
                          onClick={() => toggleArrayValue(key, option)}
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
                <span className="text-sm font-medium">禁止事項</span>
                <Textarea
                  onChange={(event) => setValue("prohibited_actions", event.target.value)}
                  value={(answers.prohibited_actions as string) ?? ""}
                />
              </label>

              <div className="space-y-3">
                <span className="text-sm font-medium">レビュー方針</span>
                <div className="flex flex-wrap gap-2">
                  {reviewPolicies.map((option) => (
                    <Button
                      key={option}
                      onClick={() => setValue("review_policy", option)}
                      type="button"
                      variant={answers.review_policy === option ? "primary" : "outline"}
                    >
                      {option}
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          ) : null}

          {step === 2 ? (
            <div className="grid gap-4">
              <label className="block space-y-2">
                <span className="text-sm font-medium">ブランチ戦略</span>
                <Input
                  onChange={(event) => setValue("branch_strategy", event.target.value)}
                  value={(answers.branch_strategy as string) ?? ""}
                />
              </label>
              <label className="block space-y-2">
                <span className="text-sm font-medium">CI コマンド</span>
                <Input
                  onChange={(event) => setValue("ci_command", event.target.value)}
                  value={(answers.ci_command as string) ?? ""}
                />
              </label>
              <label className="block space-y-2">
                <span className="text-sm font-medium">デプロイ制約</span>
                <Textarea
                  onChange={(event) => setValue("deploy_constraints", event.target.value)}
                  value={(answers.deploy_constraints as string) ?? ""}
                />
              </label>
              <label className="block space-y-2">
                <span className="text-sm font-medium">セキュリティ要件</span>
                <Textarea
                  onChange={(event) => setValue("security_requirements", event.target.value)}
                  value={(answers.security_requirements as string) ?? ""}
                />
              </label>
              <label className="block space-y-2">
                <span className="text-sm font-medium">過去の失敗事例</span>
                <Textarea
                  onChange={(event) => setValue("failure_examples", event.target.value)}
                  value={(answers.failure_examples as string) ?? ""}
                />
              </label>
              <label className="block space-y-2">
                <span className="text-sm font-medium">命名規約</span>
                <Input
                  onChange={(event) => setValue("naming_convention", event.target.value)}
                  value={(answers.naming_convention as string) ?? ""}
                />
              </label>
            </div>
          ) : null}

          {step === 3 ? (
            <div className="grid gap-4 md:grid-cols-2">
              <Card className="border-dashed">
                <CardHeader>
                  <CardTitle>選択内容</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm">
                  <p>
                    <span className="font-medium">プロジェクト名:</span> {projectName}
                  </p>
                  <p>
                    <span className="font-medium">プリセット:</span>{" "}
                    {presets.find((preset) => preset.id === selectedPresetId)?.name ?? "カスタム"}
                  </p>
                  {Object.entries(answers).map(([key, value]) => (
                    <p key={key}>
                      <span className="font-medium">{key}:</span>{" "}
                      {Array.isArray(value) ? value.join(", ") : value || "未設定"}
                    </p>
                  ))}
                </CardContent>
              </Card>

              <Card className="border-dashed">
                <CardHeader>
                  <CardTitle>生成される内容</CardTitle>
                  <CardDescription>
                    エージェントルール、ツール設定、プロンプト、品質管理、verify スクリプトを作成します。
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-2 text-sm text-muted-foreground">
                  <p>1. 回答を保存</p>
                  <p>2. Jinja2 テンプレートからファイルを生成</p>
                  <p>3. プレビュー画面へ遷移し、編集・ZIP ダウンロードを提供</p>
                </CardContent>
              </Card>
            </div>
          ) : null}

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
                {isSubmitting ? "生成中..." : "ファイル生成を実行"}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
