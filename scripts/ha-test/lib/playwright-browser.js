const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const repoRoot = path.resolve(__dirname, "../../..");
const browserRoot = path.join(repoRoot, ".playwright-browsers");

process.env.PLAYWRIGHT_BROWSERS_PATH ||= browserRoot;

function ensureChromiumBrowser(chromium) {
  const executablePath = chromium.executablePath();
  if (fs.existsSync(executablePath)) {
    return;
  }

  console.log(`Playwright Chromium is missing at ${executablePath}`);
  console.log("Installing Playwright Chromium for this environment...");

  const result = spawnSync("npx", ["playwright", "install", "chromium"], {
    cwd: repoRoot,
    env: process.env,
    stdio: "inherit",
    shell: process.platform === "win32",
  });

  if (result.status !== 0 || !fs.existsSync(executablePath)) {
    throw new Error(
      "Could not install Playwright Chromium. Run `npm run setup` or `npx playwright install chromium` and retry."
    );
  }
}

module.exports = {
  ensureChromiumBrowser,
};
