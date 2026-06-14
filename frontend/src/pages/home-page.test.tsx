import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { AppHomePage } from "@/pages/home-page";

vi.mock("@/contexts/use-auth", () => ({
  useAuth: () => ({ user: null }),
}));

describe("AppHomePage", () => {
  it("renders the hero section", () => {
    render(
      <MemoryRouter>
        <AppHomePage />
      </MemoryRouter>,
    );

    expect(screen.getByText("Japanese MVP")).toBeInTheDocument();
    expect(
      screen.getByText("AI コーディングの運用ルールを、会話の延長で組み立てる。"),
    ).toBeInTheDocument();
    expect(screen.getByText("OpenSpec change package")).toBeInTheDocument();
    expect(screen.getByText(/opsx:apply でハーネスを作成します。/)).toBeInTheDocument();
  });
});
