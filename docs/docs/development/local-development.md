---
title: Local development
layout: page
parent: Development
nav_order: 2
---

# Local Development

This workflow copies your local HaCasa build to a running Home Assistant VM so
you can visually check dashboard and integration changes without reinstalling
Home Assistant.

The local helper uses SSH to copy files into the VM and uses the Home Assistant
API to restart Home Assistant only when the Python integration code changed.

## 1. Enable SSH in the Home Assistant VM

Enable SSH access to your Home Assistant VM. The development task expects this
target by default:

```sh
root@192.168.0.204
```

Home Assistant documents this setup in the official
[Terminal & SSH app documentation](https://github.com/home-assistant/addons/blob/master/ssh/DOCS.md).
Use that guide to install the app, add your SSH key, and enable remote network
access on the SSH port.

## 2. Add your SSH public key

Add your local SSH public key to the Home Assistant VM so the task can copy
files without storing an SSH password in this repository.

First check whether you already have an SSH public key:

```sh
ls ~/.ssh/*.pub
```

If you do not have one, create a new key:

```sh
ssh-keygen -t ed25519 -C "hacasa-local-dev"
```

Print the public key:

```sh
cat ~/.ssh/id_ed25519.pub
```

Copy the full output and paste it into the Terminal & SSH app configuration in
Home Assistant:

```yaml
authorized_keys:
  - "ssh-ed25519 AAAA... hacasa-local-dev"
password: ""
```

Save the app configuration and restart the Terminal & SSH app. If the app uses a
Network section, make sure port `22` is exposed so the VS Code task can connect
to `root@192.168.0.204`.

Verify SSH from your computer:

```sh
ssh root@192.168.0.204
```

If this command asks for a password or fails, fix SSH access before continuing.

## 3. Create the local sync config

Copy the example config:

```sh
cp .ha-local.example.json .ha-local.json
```

The default config is:

```json
{
  "url": "http://192.168.0.204:8123",
  "username": "test",
  "password": "test",
  "sshHost": "192.168.0.204",
  "sshUser": "root",
  "sshPort": 22,
  "remoteConfigPath": "/config"
}
```

`.ha-local.json` is gitignored. Do not commit it.

## 4. Run a dry run

From the repository root, run:

```sh
npm run ha:sync:dry-run
```

The dry run validates `.ha-local.json`, checks the local build output, and
prints the SSH copy and restart actions it would perform.

## 5. Sync from VS Code

In VS Code, run:

```text
HA: Sync And Reload Local VM
```

You can also run the same workflow from a terminal:

```sh
npm run ha:sync
```

The task builds HaCasa, copies the dashboard files to:

```text
/config/www/community/HaCasa
```

and copies the generator integration to:

```text
/config/custom_components/hacasa_generator
```

## 6. Visually check Home Assistant

Open:

```text
http://192.168.0.204:8123
```

Log in with:

```text
test / test
```

For dashboard, theme, icon, or frontend-only changes, refresh the browser. If
Home Assistant keeps showing old frontend assets, clear the Home Assistant
frontend cache.

For Python integration changes, the task requests a Home Assistant restart. If
the restart API call fails, restart Home Assistant manually before testing.
