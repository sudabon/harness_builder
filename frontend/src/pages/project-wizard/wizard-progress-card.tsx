import { Check } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

import { steps } from "./constants";

interface WizardProgressCardProps {
  step: number;
}

export function WizardProgressCard({ step }: WizardProgressCardProps) {
  return (
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
  );
}
