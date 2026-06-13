import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { FileEditor } from "@/components/file-editor";

afterEach(cleanup);

describe("FileEditor", () => {
  it("saves the edited content", async () => {
    const onSave = vi.fn().mockResolvedValue(undefined);
    render(
      <FileEditor
        initialValue="# Original"
        isSaving={false}
        onCancel={vi.fn()}
        onSave={onSave}
      />,
    );

    fireEvent.change(screen.getByRole("textbox"), {
      target: { value: "# Edited" },
    });
    fireEvent.click(screen.getByRole("button", { name: "保存" }));

    expect(onSave).toHaveBeenCalledWith("# Edited");
  });

  it("cancels editing without saving", () => {
    const onCancel = vi.fn();
    const onSave = vi.fn();
    render(
      <FileEditor
        initialValue="# Original"
        isSaving={false}
        onCancel={onCancel}
        onSave={onSave}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "キャンセル" }));

    expect(onCancel).toHaveBeenCalled();
    expect(onSave).not.toHaveBeenCalled();
  });
});
