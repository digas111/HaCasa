# Welcome to HaCasa💜

[![Ko-fi](https://img.shields.io/badge/support_me_on_ko--fi-F16061?style=for-the-badge&logo=kofi&logoColor=f5f5f5)](https://ko-fi.com/damianeickhoff)
[![Discord](https://img.shields.io/discord/1256323927152660521?style=for-the-badge&logo=discord&logoColor=white&labelColor=%23a3aaf8&label=Chat%20on%20Discord&color=%235966f2)](https://discord.com/invite/9uMs9zCT7d)
![GitHub Release](https://img.shields.io/github/v/release/damianeickhoff/HaCasa?display_name=release&style=for-the-badge&label=Latest%20release&color=%239aaed4)
![GitHub Repo stars](https://img.shields.io/github/stars/damianeickhoff/hacasa?style=for-the-badge&logo=github&label=Github%20Stars&labelColor=%23d4b392&color=%23f9f2e9)

## What is HaCasa?
The sole purpose of HaCasa is to provide a modern, minimalistic dashboard for Home Assistant. It is designed to be easy to use and customize, while still providing a professional look and feel. The SOAP (significant other acceptance parameters) is a key aspect of the design, ensuring that the interface is not only functional and understandable but also visually appealing to everyone in your household.

## Documentation
All the documentation about downloading, installing and configuring can be found on our [documentation page](https://digas111.github.io/HaCasa/).

## Development
The fastest way to work on HaCasa is with the included devcontainer. Clone the
repo, open it in VS Code or another Dev Containers-compatible editor, and choose
`Reopen in Container`. The container installs Node dependencies, Playwright
Chromium, Docker, and Docker Compose so the Home Assistant smoke harness can run
without extra local setup. The devcontainer uses Docker-in-Docker, so the local
Dev Containers runtime must allow privileged containers.

Docker Desktop is the supported local runtime. On macOS, share the parent folder
that contains this repo in `Docker Desktop > Settings > Resources > File
Sharing` before starting the devcontainer. The workspace uses the normal Dev
Containers bind mount, so local uncommitted edits are visible inside the
devcontainer automatically.

For local development without the devcontainer, install everything needed for
the Home Assistant smoke harness with one command:

```sh
npm run setup:ha
```

Common test commands:

```sh
npm run test:ha:static
npm run test:ha:up
npm run test:ha:wait
npm run test:ha:browser
npm run test:ha:down
```

VS Code tasks are also available:

- `HA: Run Smoke Tests`
- `HA: Start Dashboard For Visual Check`
- `HA: Refresh Dashboard For Visual Check`
- `HA: Stop Home Assistant`

The visual-check tasks create a local Home Assistant test account. Log in with
`hacasa` / `hacasa`.

## HACS
HaCasa can be installed with HACS as a custom Dashboard repository:

```text
https://github.com/digas111/HaCasa
```

The HACS package is generated in `dist/`. Run `node scripts/build-hacs-dist.js` before publishing a release so the release tag contains the installable dashboard bundle.

## Credits
- Designed by [Damian Eickhoff](https://github.com/damianeickhoff)
- Logo design by [Fredrik Persson](https://github.com/fredrikpersson92)
- All the cards are created with [Button-card](https://github.com/custom-cards/button-card) from RomRaider
- And of course the community, who [contributed](https://github.com/damianeickhoff/HaCasa/graphs/contributors) in every way they can through Discord, the forums or Github.

## Contributing
Do you have a card design that fits our modern, minimalistic vibe? Share your creations with us! Check out the [Contributing](#contributing) section.
