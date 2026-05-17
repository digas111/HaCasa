const fs = require("fs");
const path = require("path");

const { copyDir } = require("./lib/copy-dir");

const repoRoot = path.resolve(__dirname, "../..");
const configRoot = path.join(repoRoot, ".ha-test/config");
const seedRoot = path.join(repoRoot, "tests/ha/seed-config");

const SAFE_FILES = [
  ".storage/core.area_registry",
  ".storage/core.entity_registry",
  ".storage/lovelace_dashboards",
  ".storage/lovelace_resources",
];

const SAFE_DIRS = [
  "dashboard/HaCasa/generated",
];

const SAFE_CONFIG_ENTRY_DOMAINS = new Set([
  "hacasa_generator",
]);

function copyFileIfExists(relativePath) {
  const source = path.join(configRoot, relativePath);
  if (!fs.existsSync(source) || !fs.statSync(source).isFile()) {
    return false;
  }

  const destination = path.join(seedRoot, relativePath);
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.copyFileSync(source, destination);
  return true;
}

function copyConfigEntriesIfExists() {
  const relativePath = ".storage/core.config_entries";
  const source = path.join(configRoot, relativePath);
  if (!fs.existsSync(source) || !fs.statSync(source).isFile()) {
    return false;
  }

  const data = JSON.parse(fs.readFileSync(source, "utf8"));
  data.data.entries = (data.data.entries || []).filter((entry) =>
    SAFE_CONFIG_ENTRY_DOMAINS.has(entry.domain)
  );

  const destination = path.join(seedRoot, relativePath);
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.writeFileSync(destination, `${JSON.stringify(data, null, 2)}\n`);
  return true;
}

function main() {
  if (!fs.existsSync(configRoot)) {
    throw new Error(`Home Assistant config does not exist: ${configRoot}`);
  }

  fs.rmSync(seedRoot, { recursive: true, force: true });
  fs.mkdirSync(seedRoot, { recursive: true });

  const copied = [];
  for (const relativePath of SAFE_FILES) {
    if (copyFileIfExists(relativePath)) copied.push(relativePath);
  }
  if (copyConfigEntriesIfExists()) copied.push(".storage/core.config_entries");

  for (const relativePath of SAFE_DIRS) {
    const source = path.join(configRoot, relativePath);
    if (fs.existsSync(source) && fs.statSync(source).isDirectory()) {
      copyDir(source, path.join(seedRoot, relativePath));
      copied.push(`${relativePath}/`);
    }
  }

  console.log(`Wrote safe Home Assistant seed to ${seedRoot}`);
  for (const item of copied) {
    console.log(`- ${item}`);
  }
}

main();
