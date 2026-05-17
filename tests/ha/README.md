# Home Assistant Dashboard Test Harness

This fixture boots Home Assistant Container with HaCasa installed under
`/config/www/community/HaCasa`, matching the path HACS uses for dashboard
repositories. A test-only `hacsfiles_test` integration registers `/hacsfiles`
to `/config/www/community`, which mirrors the static asset route HACS exposes.
It is for compatibility smoke tests only, not for production use.

## Local Usage

The recommended setup is the repo devcontainer. Clone the repository, open it in
a Dev Containers-compatible editor, and choose `Reopen in Container`. The
container installs Node dependencies, Playwright Chromium, Docker, and Docker
Compose. It uses Docker-in-Docker, so the local Dev Containers runtime must
allow privileged containers.

Docker Desktop is the supported local runtime. On macOS, share the parent folder
that contains this repo in `Docker Desktop > Settings > Resources > File
Sharing` before starting the devcontainer. The workspace uses the normal Dev
Containers bind mount, so local uncommitted edits are visible inside the
devcontainer automatically.

If you are not using the devcontainer:

1. Install Node, Playwright, and pinned Home Assistant frontend dependencies:

   ```sh
   npm run setup:ha
   ```

2. Build the HACS package, prepare `.ha-test/config`, download pinned frontend
   dependencies, and validate YAML:

   ```sh
   npm run test:ha:static
   ```

3. Start Docker Desktop or another Docker daemon.

4. Start Home Assistant:

   ```sh
   npm run test:ha:up
   ```

5. Wait for Home Assistant to answer:

   ```sh
   npm run test:ha:wait
   ```

6. Run the desktop and mobile browser smoke tests:

   ```sh
   npm run test:ha:browser
   ```

7. Stop and remove the test stack:

   ```sh
   npm run test:ha:down
   ```

The browser test completes onboarding with fixed local test credentials
(`hacasa` / `hacasa`), opens `/hacasa-dashboard/home`, checks for missing custom
cards and Lovelace errors, and writes screenshots to `.ha-test/artifacts/`.

In VS Code, run `HA: Start Dashboard For Visual Check` to prepare the fixture,
start Home Assistant, wait for it to answer, create the test account, and print
the dashboard URL. Log in with `hacasa` / `hacasa`.
After local source edits, run `HA: Refresh Dashboard For Visual Check` to
rebuild the fixture, restart Home Assistant, and print the dashboard URL again.
Run `HA: Stop Home Assistant` when finished.

## Persisting Test Home Assistant State

`npm run test:ha:prepare` rebuilds `.ha-test/config` from the repo every time.
Safe Home Assistant state can be committed under `tests/ha/seed-config`; this
directory is copied into `.ha-test/config` after the generated HaCasa package and
fixture configuration are installed.

The seed intentionally excludes auth files, tokens, UUIDs, recorder databases,
logs, and runtime locks. It currently preconfigures the `hacasa_generator`
integration so the HaCasa Generator sidebar panel is available without manually
adding the integration after each rebuild.

To refresh the committed seed from the current local HA config, run:

```sh
npm run test:ha:snapshot-seed
```

For a full local-only backup, use:

```sh
npm run test:ha:snapshot-local
```

Local backups are written to `.ha-test-backups/` and are git-ignored because
they may contain auth/session state. Restore one with:

```sh
npm run test:ha:restore-local -- .ha-test-backups/ha-config-YYYY-MM-DD.tar.gz
```

## Dependency Updates

Pinned frontend assets live in `tests/ha/dependencies.json`. Update those URLs
deliberately when validating compatibility with newer dependency releases.
