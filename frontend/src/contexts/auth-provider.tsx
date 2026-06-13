import { useEffect, useState, type PropsWithChildren } from "react";

import { ApiError, api } from "@/lib/api";

import { AuthContext, type AuthContextValue } from "./auth-context";

export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<AuthContextValue["user"]>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    api
      .me()
      .then(({ user: nextUser }) => setUser(nextUser))
      .catch((error: unknown) => {
        if (!(error instanceof ApiError) || error.status !== 401) {
          console.error(error);
        }
      })
      .finally(() => setIsLoading(false));
  }, []);

  const value: AuthContextValue = {
    user,
    isLoading,
    async login(email, password) {
      const response = await api.login(email, password);
      setUser(response.user);
    },
    async register(email, password) {
      const response = await api.register(email, password);
      setUser(response.user);
    },
    async logout() {
      await api.logout();
      setUser(null);
    },
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
