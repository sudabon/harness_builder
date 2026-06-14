import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { AnswerMap, Preset } from "@/lib/types";

interface ConfirmationStepProps {
  answers: AnswerMap;
  presets: Preset[];
  projectName: string;
  selectedPresetId: string | null;
}

export function ConfirmationStep({
  answers,
  presets,
  projectName,
  selectedPresetId,
}: ConfirmationStepProps) {
  return (
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
            エージェントルール、ツール設定、プロンプト、品質管理、verify スクリプトの下書きを含む
            OpenSpec change パッケージを作成します。
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-muted-foreground">
          <p>1. 回答を保存</p>
          <p>2. Jinja2 テンプレートから `setup-ai-harness` change を生成</p>
          <p>3. プレビュー画面へ遷移し、編集・ZIP ダウンロードを提供</p>
          <p>4. 対象リポジトリのルートに展開し、`/opsx:apply setup-ai-harness` を実行</p>
        </CardContent>
      </Card>
    </div>
  );
}
