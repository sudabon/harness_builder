import { Link } from "react-router-dom";
import { ArrowRight, Binary, FileArchive, Files, WandSparkles } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/contexts/use-auth";

const features = [
  {
    title: "プリセット起点",
    description: "FastAPI + React などのプリセットを選び、必要項目だけ微調整できます。",
    icon: WandSparkles,
  },
  {
    title: "生成後すぐ編集",
    description: "ブラウザ上で proposal や tasks を確認し、その場で修正できます。",
    icon: Files,
  },
  {
    title: "OpenSpec 適用",
    description: "change パッケージを ZIP で持ち帰り、対象リポジトリで opsx:apply します。",
    icon: FileArchive,
  },
];

export function AppHomePage() {
  const { user } = useAuth();

  return (
    <div className="shell space-y-8">
      <section className="grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
        <div className="surface overflow-hidden px-6 py-8 md:px-10 md:py-12">
          <Badge>Japanese MVP</Badge>
          <h1 className="mt-5 max-w-3xl text-4xl font-semibold tracking-tight md:text-6xl">
            AI コーディングの運用ルールを、会話の延長で組み立てる。
          </h1>
          <p className="mt-4 max-w-2xl text-base leading-7 text-muted-foreground md:text-lg">
            プロジェクト種別、利用言語、AI ツール、レビュー方針を入力すると、
            OpenSpec change パッケージを生成します。対象リポジトリで `/opsx:apply setup-ai-harness`
            を実行すると、ハーネス一式が実情に合わせて作成されます。
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Button asChild size="lg">
              <Link to={user ? "/projects/new" : "/auth"}>
                {user ? "ウィザードを開始" : "ログインして開始"}
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <a href="#flow">フローを見る</a>
            </Button>
          </div>
        </div>

        <Card className="border-secondary/20 bg-secondary text-secondary-foreground">
          <CardHeader>
            <p className="section-label text-secondary-foreground/70">Generated Outputs</p>
            <CardTitle className="text-3xl">OpenSpec change package</CardTitle>
            <CardDescription className="text-secondary-foreground/75">
              Claude / Codex / Cursor の選択に応じた下書きを tasks に同梱します。
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="rounded-3xl bg-white/12 p-4 font-mono">
              openspec/changes/setup-ai-harness/proposal.md
              <br />
              openspec/changes/setup-ai-harness/tasks.md
              <br />
              openspec/changes/setup-ai-harness/.openspec.yaml
              <br />
              specs/ai-coding-harness/spec.md
            </div>
            <div className="flex items-center gap-3 rounded-3xl bg-white/12 p-4">
              <Binary className="h-5 w-5" />
              ZIP を対象リポジトリのルートに展開し、opsx:apply でハーネスを作成します。
            </div>
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-5 md:grid-cols-3" id="flow">
        {features.map(({ title, description, icon: Icon }) => (
          <Card key={title}>
            <CardHeader>
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-accent/50">
                <Icon className="h-5 w-5" />
              </div>
              <CardTitle>{title}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-6 text-muted-foreground">{description}</p>
            </CardContent>
          </Card>
        ))}
      </section>
    </div>
  );
}
