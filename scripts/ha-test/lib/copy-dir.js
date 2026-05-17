const fs = require("fs");
const path = require("path");

const IGNORED_NAMES = new Set([".DS_Store", "__pycache__"]);

function shouldSkip(entryName) {
  return IGNORED_NAMES.has(entryName) || entryName.endsWith(".pyc");
}

function copyDir(source, destination) {
  fs.mkdirSync(destination, { recursive: true });

  if (!fs.existsSync(source)) {
    return;
  }

  for (const entry of fs.readdirSync(source, { withFileTypes: true })) {
    if (shouldSkip(entry.name)) continue;

    const sourcePath = path.join(source, entry.name);
    const destinationPath = path.join(destination, entry.name);

    if (entry.isDirectory()) {
      copyDir(sourcePath, destinationPath);
    } else if (entry.isFile()) {
      fs.copyFileSync(sourcePath, destinationPath);
    }
  }
}

module.exports = { copyDir, shouldSkip };
