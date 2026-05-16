# HaCasa Devcontainer

## Supported Runtime

Docker Desktop is the supported local runtime for the devcontainer and Home
Assistant smoke harness.

The workspace uses the normal Dev Containers bind mount. Local uncommitted edits
on the host are visible inside the devcontainer automatically.

## macOS Docker Desktop

Docker Desktop for macOS must be allowed to bind-mount the local repository
folder before VS Code can start this devcontainer.

If startup fails with `Mounts denied`, fix it in Docker Desktop:

1. Open Docker Desktop.
2. Go to `Settings > Resources > File Sharing`.
3. Add the parent folder that contains this repo, for example:

   ```text
   /Users/digas/Documents/SmartHome
   ```

4. Apply and restart Docker Desktop if prompted.
5. In VS Code, run `Dev Containers: Rebuild Container`.

## Visual Iteration

Use `HA: Start Dashboard For Visual Check` to prepare the fixture and start Home
Assistant. After local source edits, run `HA: Refresh Dashboard For Visual
Check` to rebuild the fixture, restart Home Assistant, and print the dashboard
URL again.
