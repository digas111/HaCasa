const http = require("http");

const baseUrl = process.env.HA_TEST_URL || "http://127.0.0.1:8123";
const timeoutMs = Number(process.env.HA_TEST_WAIT_MS || 180000);
const intervalMs = 3000;
const startedAt = Date.now();

function probe() {
  return new Promise((resolve) => {
    const request = http.get(`${baseUrl}/manifest.json`, (response) => {
      response.resume();
      resolve(response.statusCode >= 200 && response.statusCode < 500);
    });

    request.setTimeout(5000, () => {
      request.destroy();
      resolve(false);
    });
    request.on("error", () => resolve(false));
  });
}

async function main() {
  while (Date.now() - startedAt < timeoutMs) {
    if (await probe()) {
      console.log(`Home Assistant is reachable at ${baseUrl}`);
      return;
    }

    await new Promise((resolve) => setTimeout(resolve, intervalMs));
  }

  throw new Error(`Timed out waiting for Home Assistant at ${baseUrl}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
