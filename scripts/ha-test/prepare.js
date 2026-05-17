const fs = require("fs");
const https = require("https");
const path = require("path");

const repoRoot = path.resolve(__dirname, "../..");
const testRoot = path.join(repoRoot, ".ha-test");
const configRoot = path.join(testRoot, "config");
const hacsRoot = path.join(configRoot, "www/community");
const hacasaTarget = path.join(hacsRoot, "HaCasa");
const fixtureRoot = path.join(repoRoot, "tests/ha");
const dependencyLock = require(path.join(fixtureRoot, "dependencies.json"));

function copyDir(source, destination) {
  fs.mkdirSync(destination, { recursive: true });

  for (const entry of fs.readdirSync(source, { withFileTypes: true })) {
    if (entry.name === ".DS_Store" || entry.name === "__pycache__" || entry.name.endsWith(".pyc")) continue;

    const sourcePath = path.join(source, entry.name);
    const destinationPath = path.join(destination, entry.name);

    if (entry.isDirectory()) {
      copyDir(sourcePath, destinationPath);
    } else if (entry.isFile()) {
      fs.copyFileSync(sourcePath, destinationPath);
    }
  }
}

function download(url, destination, redirectCount = 0) {
  if (redirectCount > 5) {
    return Promise.reject(new Error(`Too many redirects while downloading ${url}`));
  }

  fs.mkdirSync(path.dirname(destination), { recursive: true });

  return new Promise((resolve, reject) => {
    const request = https.get(url, { headers: { "User-Agent": "HaCasa test harness" } }, (response) => {
      if ([301, 302, 303, 307, 308].includes(response.statusCode)) {
        response.resume();
        download(response.headers.location, destination, redirectCount + 1).then(resolve, reject);
        return;
      }

      if (response.statusCode !== 200) {
        response.resume();
        reject(new Error(`Download failed (${response.statusCode}) for ${url}`));
        return;
      }

      const file = fs.createWriteStream(destination);
      response.pipe(file);
      file.on("finish", () => {
        file.close(resolve);
      });
      file.on("error", reject);
    });

    request.on("error", reject);
  });
}

async function main() {
  fs.rmSync(testRoot, { recursive: true, force: true });
  fs.mkdirSync(configRoot, { recursive: true });

  copyDir(path.join(repoRoot, "dist"), hacasaTarget);

  const viewTarget = path.join(hacasaTarget, "dashboard/HaCasa/views");
  fs.rmSync(viewTarget, { recursive: true, force: true });
  copyDir(path.join(fixtureRoot, "views"), viewTarget);

  fs.copyFileSync(
    path.join(fixtureRoot, "configuration.yaml"),
    path.join(configRoot, "configuration.yaml")
  );
  copyDir(path.join(fixtureRoot, "custom_components"), path.join(configRoot, "custom_components"));
  const integrationSource = path.join(repoRoot, "dist/custom_components");
  if (fs.existsSync(integrationSource)) {
    copyDir(integrationSource, path.join(configRoot, "custom_components"));
  }

  for (const dependency of dependencyLock.dependencies) {
    const target = path.join(hacsRoot, dependency.target);
    console.log(`Downloading ${dependency.name}@${dependency.version}`);
    await download(dependency.url, target);
  }

  fs.mkdirSync(path.join(testRoot, "artifacts"), { recursive: true });
  console.log(`Prepared Home Assistant test config at ${configRoot}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
