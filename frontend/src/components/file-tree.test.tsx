import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { FileTree } from "@/components/file-tree";
import type { GeneratedFileSummary } from "@/lib/types";

const files: GeneratedFileSummary[] = [
  {
    id: "file-1",
    file_path: "AGENTS.md",
    is_edited: true,
    created_at: "2026-06-13T00:00:00Z",
    updated_at: "2026-06-13T00:00:00Z",
  },
  {
    id: "file-2",
    file_path: "PROJECT_RULES.md",
    is_edited: false,
    created_at: "2026-06-13T00:00:00Z",
    updated_at: "2026-06-13T00:00:00Z",
  },
];

describe("FileTree", () => {
  it("shows an edited badge only for edited files", () => {
    render(<FileTree files={files} onSelect={vi.fn()} selectedFileId={null} />);

    expect(screen.getByText("AGENTS.md")).toBeInTheDocument();
    expect(screen.getByText("PROJECT_RULES.md")).toBeInTheDocument();
    expect(screen.getAllByText("編集済み")).toHaveLength(1);

    const editedButton = screen.getByText("AGENTS.md").closest("button");
    expect(editedButton).not.toBeNull();
    expect(editedButton!.textContent).toContain("編集済み");
  });
});
