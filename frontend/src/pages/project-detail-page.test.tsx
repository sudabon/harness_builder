import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

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

afterEach(cleanup);

describe("ProjectDetailPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(api.getProject).mockResolvedValue(project);
    vi.mocked(api.listFiles).mockResolvedValue({ items: [tasksFile] });
    vi.mocked(api.getFile).mockResolvedValue({ ...tasksFile, content: "# Tasks\n" });
  });

  function renderPage() {
    render(
      <MemoryRouter initialEntries={["/projects/project-1"]}>
        <Routes>
          <Route path="/projects/:id" element={<ProjectDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );
  }

  it("shows OpenSpec change usage guidance", async () => {
    renderPage();

    expect(await screen.findByText("使い方")).toBeInTheDocument();
    expect(screen.getByText(/ZIP を対象リポジトリのルートに展開/)).toBeInTheDocument();
    expect(screen.getByText(/\/opsx:apply setup-ai-harness/)).toBeInTheDocument();
  });

  it.each([
    ["保護のまま再生成", false],
    ["上書きして再生成", true],
  ])("passes force=%s from the edited-file confirmation", async (buttonLabel, force) => {
    const editedTasksFile = { ...tasksFile, is_edited: true };
    vi.mocked(api.listFiles).mockResolvedValue({ items: [editedTasksFile] });
    vi.mocked(api.getFile).mockResolvedValue({
      ...editedTasksFile,
      content: "# Edited Tasks\n",
    });
    vi.mocked(api.generateFiles).mockResolvedValue({ items: [editedTasksFile] });

    renderPage();

    fireEvent.click(await screen.findByRole("button", { name: /再生成/ }));
    expect(await screen.findByText("編集済みファイルがあります")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: buttonLabel }));

    await waitFor(() => {
      expect(api.generateFiles).toHaveBeenCalledWith("project-1", force);
    });
  });
});
