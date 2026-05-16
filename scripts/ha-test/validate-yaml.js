const fs = require("fs");
const path = require("path");
const YAML = require("yaml");

const repoRoot = path.resolve(__dirname, "../..");
const pathsToValidate = [
  "tests/ha/configuration.yaml",
  "tests/ha/views/00-smoke.yaml",
  "dist/dashboard/HaCasa/main.yaml",
];

function normalizeHomeAssistantTags(source) {
  return source.replace(/!include(?:_dir_merge_named|_dir_list|_dir_named|_dir_merge_list)?\s+([^\n]+)/g, (_match, includePath) => {
    return JSON.stringify(includePath.trim());
  });
}

let hasError = false;

for (const relativePath of pathsToValidate) {
  const filePath = path.join(repoRoot, relativePath);
  const source = fs.readFileSync(filePath, "utf8");
  const doc = YAML.parseDocument(normalizeHomeAssistantTags(source), {
    prettyErrors: true,
  });

  if (doc.errors.length > 0) {
    hasError = true;
    console.error(`YAML errors in ${relativePath}`);
    for (const error of doc.errors) {
      console.error(error.message);
    }
  } else {
    console.log(`YAML OK: ${relativePath}`);
  }
}

if (hasError) {
  process.exit(1);
}
