import { expect, test, type Page } from "@playwright/test";

async function registerAndEnterWizard(page: Page, suffix: string) {
  await page.goto("/auth");
  await page.getByRole("button", { name: "新規登録" }).click();
  await page.getByLabel("メールアドレス").fill(`user-${suffix}@example.com`);
  await page.getByLabel("パスワード").fill("supersecret");
  await page.getByRole("button", { name: "新規登録して開始" }).click();
  await expect(page).toHaveURL(/\/projects\/new$/);
}

async function generateProjectWithPreset(page: Page, suffix: string) {
  await registerAndEnterWizard(page, suffix);
  await page.getByText("FastAPI + React").click();
  await page.getByRole("button", { name: "次へ" }).click();
  await page.getByLabel("禁止事項").fill("本番DBの直接変更禁止");
  await page.getByRole("button", { name: "次へ" }).click();
  await page.getByLabel("ブランチ戦略").fill("trunk-based");
  await page.getByLabel("CI コマンド").fill("pnpm test && uv run pytest");
  await page.getByRole("button", { name: "次へ" }).click();
}

test("wizard flow generates files and supports ZIP download", async ({ page }) => {
  await generateProjectWithPreset(page, `flow-${Date.now()}`);

  await page.getByRole("button", { name: "ファイル生成を実行" }).click();

  await expect(page).toHaveURL(/\/projects\/.+/);
  await expect(page.getByText("AGENTS.md")).toBeVisible();

  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "ZIP" }).click();
  const download = await downloadPromise;

  expect(download.suggestedFilename()).toContain(".zip");
});

test("preset selection pre-fills the review summary", async ({ page }) => {
  await generateProjectWithPreset(page, `preset-${Date.now()}`);

  await expect(page.getByText("FastAPI, React")).toBeVisible();
  await expect(page.getByText("pytest, jest")).toBeVisible();
  await expect(page.getByText("ruff, eslint, prettier")).toBeVisible();
});

test("edited file can be saved before ZIP download", async ({ page }) => {
  await generateProjectWithPreset(page, `edit-${Date.now()}`);
  await page.getByRole("button", { name: "ファイル生成を実行" }).click();

  await expect(page).toHaveURL(/\/projects\/.+/);
  await page.getByRole("button", { name: "編集" }).click();

  const editor = page.locator("textarea");
  await editor.fill("# Playwright Updated\n");
  await page.getByRole("button", { name: "保存" }).click();

  await expect(page.getByText("ファイルを保存しました。")).toBeVisible();

  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "ZIP" }).click();
  await downloadPromise;
  await expect(page.getByText("ZIP ダウンロードを開始しました。")).toBeVisible();
});
