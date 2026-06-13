import { Link, NavLink, Outlet } from "react-router-dom";
import { ArrowRight, LogOut, Sparkles } from "lucide-react";

import { useAuth } from "@/contexts/use-auth";
import { Button } from "@/components/ui/button";

export function Layout() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen">
      <header className="shell">
        <div className="surface flex flex-col gap-4 px-6 py-5 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-4">
            <Link className="flex items-center gap-3" to="/">
              <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-primary text-primary-foreground">
                <Sparkles className="h-5 w-5" />
              </div>
              <div>
                <p className="section-label">Harness Builder</p>
                <p className="text-lg font-semibold">AI 開発ルールを最短で構築</p>
              </div>
            </Link>
          </div>

          <nav className="flex flex-wrap items-center gap-3 text-sm">
            <NavLink className="rounded-full px-4 py-2 hover:bg-muted" to="/">
              ホーム
            </NavLink>
            <NavLink className="rounded-full px-4 py-2 hover:bg-muted" to="/projects/new">
              新規作成
            </NavLink>
            {user ? (
              <>
                <span className="rounded-full bg-muted px-4 py-2 text-muted-foreground">
                  {user.email}
                </span>
                <Button onClick={() => void logout()} size="sm" variant="ghost">
                  <LogOut className="h-4 w-4" />
                  ログアウト
                </Button>
              </>
            ) : (
              <Button asChild size="sm">
                <Link to="/auth">
                  ログイン
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </Button>
            )}
          </nav>
        </div>
      </header>

      <main className="pb-16">
        <Outlet />
      </main>
    </div>
  );
}
