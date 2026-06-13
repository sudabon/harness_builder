import { useState, type FormEvent } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/contexts/use-auth";

type Mode = "login" | "register";

export function AuthPage() {
  const [mode, setMode] = useState<Mode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { login, register } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const nextPath = (location.state as { from?: string } | null)?.from ?? "/projects/new";

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      if (mode === "login") {
        await login(email, password);
      } else {
        await register(email, password);
      }
      navigate(nextPath, { replace: true });
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "認証に失敗しました。");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="shell grid gap-6 lg:grid-cols-[1fr_1.1fr]">
      <Card className="bg-secondary text-secondary-foreground">
        <CardHeader>
          <p className="section-label text-secondary-foreground/70">Access Control</p>
          <CardTitle className="text-4xl">プロジェクトごとの生成物を安全に管理</CardTitle>
          <CardDescription className="text-secondary-foreground/75">
            MVP ではメールアドレス + パスワードのシンプルなセッション認証を採用しています。
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 text-sm">
          <div className="rounded-3xl bg-white/10 p-4">
            新規登録後はそのままセッションが発行され、ウィザードに移動します。
          </div>
          <div className="rounded-3xl bg-white/10 p-4">
            生成したファイル、編集内容、ZIP エクスポートはログインユーザーに紐づきます。
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex gap-2">
            <Button
              type="button"
              onClick={() => setMode("login")}
              variant={mode === "login" ? "primary" : "outline"}
            >
              ログイン
            </Button>
            <Button
              type="button"
              onClick={() => setMode("register")}
              variant={mode === "register" ? "primary" : "outline"}
            >
              新規登録
            </Button>
          </div>
          <CardTitle>{mode === "login" ? "既存アカウントで開始" : "新しいアカウントを作成"}</CardTitle>
          <CardDescription>
            {mode === "login"
              ? "保存済みプロジェクトを再編集できます。"
              : "初回利用の場合はこちらから登録してください。"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form className="space-y-4" onSubmit={handleSubmit}>
            <label className="block space-y-2 text-sm">
              <span>メールアドレス</span>
              <Input
                autoComplete="email"
                onChange={(event) => setEmail(event.target.value)}
                placeholder="team@example.com"
                type="email"
                value={email}
              />
            </label>
            <label className="block space-y-2 text-sm">
              <span>パスワード</span>
              <Input
                autoComplete={mode === "login" ? "current-password" : "new-password"}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="8文字以上"
                type="password"
                value={password}
              />
            </label>

            {error ? <p className="text-sm text-danger">{error}</p> : null}

            <Button className="w-full" disabled={isSubmitting} type="submit">
              {isSubmitting ? "送信中..." : mode === "login" ? "ログイン" : "新規登録して開始"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
