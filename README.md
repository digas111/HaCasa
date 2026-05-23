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
Install the Node dependencies with:

```sh
npm run setup
```

Home Assistant integration tests use pytest and require Python 3.14.2 or newer,
matching the current Home Assistant development environment. Install the pinned
test dependencies in a Python 3.14 virtual environment:

```sh
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-test.txt
```

Common test commands:

```sh
npm run test:static
npm run test:python
npm test
```

The automated test workflow does not start, onboard, or manage a Home Assistant
instance. Tests run against Home Assistant's pytest fixtures.

### Manual Home Assistant VM testing

For visual checks, use a persistent local Home Assistant OS VM with SSH access.
The default local development target is `root@192.168.0.204` and the Home
Assistant URL is `http://192.168.0.204:8123`.

1. Copy `.ha-local.example.json` to `.ha-local.json`.
2. Confirm the SSH and Home Assistant settings in `.ha-local.json`.
3. Configure HaCasa once in the VM's `configuration.yaml`.
4. Sync repo changes into the VM:

   ```sh
   npm run ha:sync
   ```

Use `npm run ha:sync:dry-run` to verify the SSH/API actions before copying.
The sync task restarts Home Assistant only when the Python integration code
changed. For dashboard/frontend-only changes, refresh the browser and clear the
Home Assistant frontend cache if needed.

See the [local development guide](docs/docs/development/local-development.md) for
the full setup.

## HACS
HaCasa can be installed with HACS as a custom Integration repository:

```text
https://github.com/digas111/HaCasa
```

## Credits
- Designed by [Damian Eickhoff](https://github.com/damianeickhoff)
- Logo design by [Fredrik Persson](https://github.com/fredrikpersson92)
- All the cards are created with [Button-card](https://github.com/custom-cards/button-card) from RomRaider
- And of course the community, who [contributed](https://github.com/damianeickhoff/HaCasa/graphs/contributors) in every way they can through Discord, the forums or Github.

## Contributing
Do you have a card design that fits our modern, minimalistic vibe? Share your creations with us! Check out the [Contributing](#contributing) section.
