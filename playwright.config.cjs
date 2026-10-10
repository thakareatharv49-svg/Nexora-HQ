const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./tests/e2e",
  reporter: "list",
  timeout: 30_000,
  use: {
    baseURL: "http://127.0.0.1:8001",
    headless: true,
  },
  webServer: {
    command: "python -m uvicorn src.nexora_hq.app:app --host 127.0.0.1 --port 8001",
    url: "http://127.0.0.1:8001/api/health",
    reuseExistingServer: false,
    timeout: 60_000,
    env: process.env,
  },
});
