import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "@/lib/api";
import { ProjectDetailPage } from "@/pages/project-detail-page";

vi.mock("@/lib/api", () => ({
  api: {
    exportProject: vi.fn(),
    generateFiles: vi.fn(),
    getFile: vi.fn(),
    getProject: vi.fn(),
    listFiles: vi.fn(),
    updateFile: vi.fn(),
  },
}));

const project = {
  id: "project-1",
  name: "Harness Demo",
  preset_id: "fastapi-react",
  answers: {},
  created_at: "2026-06-13T00:00:00Z",
  updated_at: "2026-06-13T00:00:00Z",
};

const tasksFile = {
  id: "file-1",
  file_path: "openspec/changes/setup-ai-harness/tasks.md",
  is_edited: false,
  created_at: "2026-06-13T00:00:00Z",
  updated_at: "2026-06-13T00:00:00Z",
};

describe("ProjectDetailPage", () => {
  beforeEach(() => {
    vi.mocked(api.getProject).mockResolvedValue(project);
    vi.mocked(api.listFiles).mockResolvedValue({ items: [tasksFile] });
    vi.mocked(api.getFile).mockResolvedValue({ ...tasksFile, content: "# Tasks\n" });
  });

  it("shows OpenSpec change usage guidance", async () => {
    render(
      <MemoryRouter initialEntries={["/projects/project-1"]}>
        <Routes>
          <Route path="/projects/:id" element={<ProjectDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText("使い方")).toBeInTheDocument();
    expect(screen.getByText(/ZIP を対象リポジトリのルートに展開/)).toBeInTheDocument();
    expect(screen.getByText(/\/opsx:apply setup-ai-harness/)).toBeInTheDocument();
  });
});
