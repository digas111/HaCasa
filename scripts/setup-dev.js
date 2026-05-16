const { spawnSync } = require("child_process");
const path = require("path");

const repoRoot = path.resolve(__dirname, "..");
process.env.PLAYWRIGHT_BROWSERS_PATH = path.join(repoRoot, ".playwright-browsers");

const installSystemDeps = process.argv.includes("--with-system-deps");

function run(command, args) {
  const result = spawnSync(command, args, {
    stdio: "inherit",
    shell: process.platform === "win32",
  });

  if (result.status !== 0) {
    process.exit(result.status || 1);
  }
}

run("npm", ["ci"]);

const playwrightArgs = ["playwright", "install"];
if (installSystemDeps) {
  playwrightArgs.push("--with-deps");
}
playwrightArgs.push("chromium");

run("npx", playwrightArgs);

console.log("");
console.log("Development dependencies installed.");
