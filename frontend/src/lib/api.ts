import type {
  GeneratedFile,
  GeneratedFilesList,
  Preset,
  Project,
  User,
} from "@/lib/types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(init.headers ?? {}),
    },
    ...init,
  });

  if (response.status === 204) {
    return undefined as T;
  }

  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail =
      typeof body?.detail === "string" ? body.detail : "リクエストの処理に失敗しました。";
    throw new ApiError(detail, response.status);
  }

  return body as T;
}

export const api = {
  async register(email: string, password: string) {
    return request<{ user: User }>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  },
  async login(email: string, password: string) {
    return request<{ user: User }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  },
  async logout() {
    return request<void>("/auth/logout", { method: "POST" });
  },
  async me() {
    return request<{ user: User }>("/auth/me");
  },
  async listPresets() {
    return request<Preset[]>("/presets");
  },
  async createProject(payload: { name: string; preset_id?: string | null }) {
    return request<Project>("/projects", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  async getProject(id: string) {
    return request<Project>(`/projects/${id}`);
  },
  async updateAnswers(id: string, answers: Project["answers"]) {
    return request<Project>(`/projects/${id}/answers`, {
      method: "PUT",
      body: JSON.stringify({ answers }),
    });
  },
  async generateFiles(id: string, force = false) {
    return request<GeneratedFilesList>(`/projects/${id}/generate`, {
      method: "POST",
      body: JSON.stringify({ force }),
    });
  },
  async listFiles(id: string) {
    return request<GeneratedFilesList>(`/projects/${id}/files`);
  },
  async getFile(projectId: string, fileId: string) {
    return request<GeneratedFile>(`/projects/${projectId}/files/${fileId}`);
  },
  async updateFile(projectId: string, fileId: string, content: string) {
    return request<GeneratedFile>(`/projects/${projectId}/files/${fileId}`, {
      method: "PUT",
      body: JSON.stringify({ content }),
    });
  },
  async exportProject(projectId: string) {
    const response = await fetch(`${API_URL}/projects/${projectId}/export`, {
      credentials: "include",
    });
    if (!response.ok) {
      throw new ApiError("ZIP エクスポートに失敗しました。", response.status);
    }

    return {
      blob: await response.blob(),
      filename:
        response.headers
          .get("Content-Disposition")
          ?.match(/filename="(.+)"/)?.[1] ?? "harness.zip",
    };
  },
};
