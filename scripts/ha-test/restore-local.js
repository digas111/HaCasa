const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const repoRoot = path.resolve(__dirname, "../..");
const configRoot = path.join(repoRoot, ".ha-test/config");
const backupRoot = path.join(repoRoot, ".ha-test-backups");

async function main() {
  const backup = process.argv[2];
  if (!backup) {
    throw new Error("Usage: node scripts/ha-test/restore-local.js .ha-test-backups/ha-config-...tar.gz");
  }

  const backupPath = path.isAbsolute(backup) ? backup : path.join(repoRoot, backup);
  if (!backupPath.startsWith(backupRoot) || !fs.existsSync(backupPath)) {
    throw new Error(`Backup must exist under ${backupRoot}`);
  }

  fs.rmSync(configRoot, { recursive: true, force: true });
  fs.mkdirSync(configRoot, { recursive: true });

  execFileSync("tar", ["-xzf", backupPath, "-C", configRoot]);
  console.log(`Restored private local Home Assistant backup into ${configRoot}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
