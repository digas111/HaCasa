const fs = require("fs");
const path = require("path");
const YAML = require("yaml");

const repoRoot = path.resolve(__dirname, "..");

const rootsToValidate = [
  "HaCasa/dashboard",
  "HaCasa/themes",
  "dist/dashboard",
  "dist/themes",
];

function collectYamlFiles(root) {
  const absoluteRoot = path.join(repoRoot, root);
  if (!fs.existsSync(absoluteRoot)) {
    return [];
  }

  const files = [];
  for (const entry of fs.readdirSync(absoluteRoot, { withFileTypes: true })) {
    const absolutePath = path.join(absoluteRoot, entry.name);
    const relativePath = path.relative(repoRoot, absolutePath);

    if (entry.isDirectory()) {
      files.push(...collectYamlFiles(relativePath));
    } else if (entry.isFile() && /\.ya?ml$/i.test(entry.name)) {
      files.push(relativePath);
    }
  }
  return files;
}

function normalizeHomeAssistantTags(source) {
  return source.replace(
    /!include(?:_dir_merge_named|_dir_merge_list|_dir_named|_dir_list)?\s+([^\n]+)/g,
    (_match, includePath) => JSON.stringify(includePath.trim())
  );
}

const pathsToValidate = rootsToValidate.flatMap(collectYamlFiles).sort();
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
  }
}

if (hasError) {
  process.exit(1);
}

console.log(`YAML OK: ${pathsToValidate.length} files`);
