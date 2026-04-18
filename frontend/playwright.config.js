import { defineConfig } from "@playwright/test";
export default defineConfig({
    testDir: "./tests/e2e",
    use: {
        baseURL: "http://localhost:5173",
        trace: "on-first-retry",
    },
    webServer: [
        {
            command: "uv run uvicorn app.main:app --host 127.0.0.1 --port 8000",
            cwd: "../backend",
            url: "http://127.0.0.1:8000/healthz",
            reuseExistingServer: !process.env.CI,
            timeout: 120000,
        },
        {
            command: "pnpm dev",
            url: "http://localhost:5173",
            cwd: ".",
            reuseExistingServer: !process.env.CI,
            timeout: 120000,
        },
    ],
});
