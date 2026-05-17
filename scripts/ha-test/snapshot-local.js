const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const repoRoot = path.resolve(__dirname, "../..");
const configRoot = path.join(repoRoot, ".ha-test/config");
const backupRoot = path.join(repoRoot, ".ha-test-backups");

async function main() {
  if (!fs.existsSync(configRoot)) {
    throw new Error(`Home Assistant config does not exist: ${configRoot}`);
  }

  fs.mkdirSync(backupRoot, { recursive: true });
  const stamp = new Date().toISOString().replace(/[:.]/g, "-");
  const target = path.join(backupRoot, `ha-config-${stamp}.tar.gz`);

  execFileSync("tar", [
    "--exclude=home-assistant.log*",
    "-czf",
    target,
    "-C",
    configRoot,
    ".",
  ]);

  console.log(`Wrote private local Home Assistant backup: ${target}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
