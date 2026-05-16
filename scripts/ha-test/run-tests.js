const { spawnSync } = require("child_process");

function run(command, args) {
  const result = spawnSync(command, args, {
    stdio: "inherit",
    shell: process.platform === "win32",
  });

  return result.status || 0;
}

let exitCode = run("npm", ["run", "test:ha:static"]);

if (exitCode === 0) {
  exitCode = run("npm", ["run", "test:ha:up"]);
}

if (exitCode === 0) {
  exitCode = run("npm", ["run", "test:ha:wait"]);
}

if (exitCode === 0) {
  exitCode = run("npm", ["run", "test:ha:browser"]);
}

const downExitCode = run("npm", ["run", "test:ha:down"]);

if (exitCode !== 0) {
  process.exit(exitCode);
}

process.exit(downExitCode);
