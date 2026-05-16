const path = require("path");

const repoRoot = path.resolve(__dirname, "../..");
process.env.PLAYWRIGHT_BROWSERS_PATH ||= path.join(repoRoot, ".playwright-browsers");

const { chromium } = require("@playwright/test");

const baseUrl = process.env.HA_TEST_URL || "http://127.0.0.1:8123";
const username = process.env.HA_TEST_USERNAME || "hacasa";
const password = process.env.HA_TEST_PASSWORD || "hacasa";
const dashboardPath = "/hacasa-dashboard/home";

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

async function main() {
  const browser = await chromium.launch();

  try {
    const page = await browser.newPage();
    await completeOnboarding(page);
    await loginIfNeeded(page);
  } finally {
    await browser.close();
  }

  console.log(`Home Assistant test user is ready: ${username} / ${password}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
