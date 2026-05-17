const fs = require("fs");
const path = require("path");

const repoRoot = path.resolve(__dirname, "../..");
process.env.PLAYWRIGHT_BROWSERS_PATH ||= path.join(repoRoot, ".playwright-browsers");

const { chromium } = require("@playwright/test");
const { ensureChromiumBrowser } = require("./lib/playwright-browser");

const artifactRoot = path.join(repoRoot, ".ha-test/artifacts");
const baseUrl = process.env.HA_TEST_URL || "http://127.0.0.1:8123";
const username = process.env.HA_TEST_USERNAME || "hacasa";
const password = process.env.HA_TEST_PASSWORD || "hacasa";
const dashboardPath = "/hacasa-dashboard/home";

const fatalPatterns = [
  /custom element doesn't exist/i,
  /failed to load resource/i,
  /error while loading/i,
  /button-card/i,
  /my-slider/i,
  /card-mod/i,
  /mini-graph/i,
  /layout-card/i,
  /kiosk-mode/i,
  /HaCasa\.js/i,
];

async function clickIfVisible(page, label, timeout = 3000) {
  const locator = page.getByRole("button", { name: label });
  if (await locator.first().isVisible({ timeout }).catch(() => false)) {
    await locator.first().click();
    return true;
  }
  return false;
}

async function completeOnboarding(page) {
  await page.goto(baseUrl, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("networkidle").catch(() => {});

  const createAccount = page.getByRole("button", { name: /create account/i });
  if (!(await createAccount.isVisible({ timeout: 8000 }).catch(() => false))) {
    return;
  }

  await page.getByLabel(/name/i).fill("HaCasa Test");
  await page.getByLabel(/username/i).fill(username);
  await page.getByLabel(/^password$/i).fill(password);
  await page.getByLabel(/confirm password/i).fill(password);
  await createAccount.click();

  for (let step = 0; step < 8; step += 1) {
    await page.waitForTimeout(1000);
    if (await clickIfVisible(page, /next/i, 1000)) continue;
    if (await clickIfVisible(page, /skip/i, 1000)) continue;
    if (await clickIfVisible(page, /finish/i, 1000)) continue;
    if (await clickIfVisible(page, /finish setup/i, 1000)) continue;
    break;
  }
}

async function loginIfNeeded(page) {
  await page.goto(`${baseUrl}${dashboardPath}`, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("networkidle").catch(() => {});

  const usernameField = page.getByLabel(/username/i);
  if (await usernameField.isVisible({ timeout: 5000 }).catch(() => false)) {
    await usernameField.fill(username);
    await page.getByLabel(/^password$/i).fill(password);
    await page.getByRole("button", { name: /log in|login|sign in/i }).click();
    await page.waitForLoadState("networkidle").catch(() => {});
  }
}

async function assertDashboard(page) {
  await page.goto(`${baseUrl}${dashboardPath}`, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("networkidle").catch(() => {});
  await page.waitForTimeout(5000);

  await page.getByText("HaCasa Smoke Test").first().waitFor({ timeout: 30000 });

  const errorCards = await page.locator("hui-error-card, .error, [class*='error']").allTextContents();
  const relevantErrors = errorCards
    .map((text) => text.trim())
    .filter((text) => text && fatalPatterns.some((pattern) => pattern.test(text)));

  if (relevantErrors.length > 0) {
    throw new Error(`Dashboard rendered errors:\n${relevantErrors.join("\n")}`);
  }
}

async function runViewport(browser, viewportName, contextOptions) {
  const pageErrors = [];
  const context = await browser.newContext(contextOptions);
  const page = await context.newPage();

  page.on("console", (message) => {
    const text = message.text();
    if (message.type() === "error" && fatalPatterns.some((pattern) => pattern.test(text))) {
      pageErrors.push(`console: ${text}`);
    }
  });
  page.on("pageerror", (error) => {
    pageErrors.push(`pageerror: ${error.message}`);
  });
  page.on("response", (response) => {
    const url = response.url();
    if ((url.includes("/hacsfiles/") || url.includes("/local/")) && response.status() >= 400) {
      pageErrors.push(`response ${response.status()}: ${url}`);
    }
  });
  page.on("requestfailed", (request) => {
    const url = request.url();
    if (url.includes("/hacsfiles/") || url.includes("/local/")) {
      pageErrors.push(`request failed: ${url} ${request.failure()?.errorText || ""}`);
    }
  });

  await completeOnboarding(page);
  await loginIfNeeded(page);
  await assertDashboard(page);

  fs.mkdirSync(artifactRoot, { recursive: true });
  await page.screenshot({
    path: path.join(artifactRoot, `${viewportName}.png`),
    fullPage: true,
  });

  await context.close();

  if (pageErrors.length > 0) {
    throw new Error(`Browser errors in ${viewportName}:\n${pageErrors.join("\n")}`);
  }
}

async function main() {
  ensureChromiumBrowser(chromium);
  const browser = await chromium.launch();

  try {
    await runViewport(browser, "desktop", { viewport: { width: 1440, height: 1100 } });
    await runViewport(browser, "mobile", {
      viewport: { width: 390, height: 844 },
      isMobile: true,
    });
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
