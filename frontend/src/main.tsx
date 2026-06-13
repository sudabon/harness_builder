import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

import { Layout } from "@/components/layout";
import { ProtectedRoute } from "@/components/protected-route";
import { AuthProvider } from "@/contexts/auth-provider";
import { AppHomePage } from "@/pages/home-page";
import { AuthPage } from "@/pages/auth-page";
import { ProjectDetailPage } from "@/pages/project-detail-page";
import { ProjectWizardPage } from "@/pages/project-wizard-page";

import "./index.css";

const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      { path: "/", element: <AppHomePage /> },
      { path: "/auth", element: <AuthPage /> },
      {
        path: "/projects/new",
        element: (
          <ProtectedRoute>
            <ProjectWizardPage />
          </ProtectedRoute>
        ),
      },
      {
        path: "/projects/:id",
        element: (
          <ProtectedRoute>
            <ProjectDetailPage />
          </ProtectedRoute>
        ),
      },
    ],
  },
]);

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  </StrictMode>,
);
