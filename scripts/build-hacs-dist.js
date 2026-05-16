const fs = require("fs");
const path = require("path");

const repoRoot = path.resolve(__dirname, "..");
const sourceRoot = path.join(repoRoot, "HaCasa");
const distRoot = path.join(repoRoot, "dist");

function copyDir(source, destination) {
  fs.mkdirSync(destination, { recursive: true });

  for (const entry of fs.readdirSync(source, { withFileTypes: true })) {
    if (entry.name === ".DS_Store") continue;

    const sourcePath = path.join(source, entry.name);
    const destinationPath = path.join(destination, entry.name);

    if (entry.isDirectory()) {
      copyDir(sourcePath, destinationPath);
    } else if (entry.isFile()) {
      fs.copyFileSync(sourcePath, destinationPath);
    }
  }
}

function extractIcon(svg) {
  const viewBoxMatch = svg.match(/viewBox=["']([^"']+)["']/i);
  const pathMatches = [...svg.matchAll(/<path\b[^>]*\bd=["']([^"']+)["'][^>]*>/gi)];

  if (pathMatches.length === 0) {
    return null;
  }

  const icon = {
    path: pathMatches.map((match) => match[1].trim()).join(" "),
  };

  if (viewBoxMatch) {
    icon.viewBox = viewBoxMatch[1];
  }

  return icon;
}

function buildIconMap() {
  const iconDir = path.join(sourceRoot, "custom_icons");
  const icons = {};

  for (const fileName of fs.readdirSync(iconDir).sort()) {
    if (!fileName.endsWith(".svg")) continue;

    const svg = fs.readFileSync(path.join(iconDir, fileName), "utf8");
    const icon = extractIcon(svg);

    if (!icon) {
      throw new Error(`Could not extract path data from ${fileName}`);
    }

    icons[path.basename(fileName, ".svg")] = icon;
  }

  icons.music = icons["music-alt"];

  return icons;
}

function writeFrontendModule() {
  const icons = buildIconMap();
  const module = `const ICONS = ${JSON.stringify(icons, null, 2)};

async function getHaCasaIcon(name) {
  return ICONS[name];
}

window.customIconsets = window.customIconsets || {};
window.customIconsets.hacasa = getHaCasaIcon;

if (!window.customIconsets.fapro) {
  window.customIconsets.fapro = getHaCasaIcon;
}

window.HaCasa = {
  ...(window.HaCasa || {}),
  assetPath: "/hacsfiles/HaCasa/images",
  version: "${fs.readFileSync(path.join(sourceRoot, "dashboard/HaCasa/VERSION.txt"), "utf8").trim()}"
};

console.info("%c HaCasa loaded", "color: #d4b392; font-weight: 700;");
`;

  fs.writeFileSync(path.join(distRoot, "HaCasa.js"), module);
}

function rewriteDashboardEntrypoint() {
  const mainPath = path.join(distRoot, "dashboard/HaCasa/main.yaml");
  const mainYaml = fs.readFileSync(mainPath, "utf8")
    .replace(
      'button_card_templates: !include_dir_merge_named "/config/dashboard/HaCasa/templates/"',
      'button_card_templates: !include_dir_merge_named "/config/www/community/HaCasa/dashboard/HaCasa/templates/"'
    )
    .replace(
      'views: !include_dir_list "/config/dashboard/HaCasa/views/"',
      'views: !include_dir_list "/config/www/community/HaCasa/dashboard/HaCasa/views/"'
    );

  fs.writeFileSync(mainPath, mainYaml);
}

fs.rmSync(distRoot, { recursive: true, force: true });
fs.mkdirSync(distRoot, { recursive: true });

copyDir(path.join(sourceRoot, "dashboard"), path.join(distRoot, "dashboard"));
copyDir(path.join(sourceRoot, "themes"), path.join(distRoot, "themes"));
copyDir(path.join(sourceRoot, "www/images"), path.join(distRoot, "images"));
copyDir(path.join(sourceRoot, "custom_icons"), path.join(distRoot, "custom_icons"));

rewriteDashboardEntrypoint();
writeFrontendModule();
