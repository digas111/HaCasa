---
title: Downloads
layout: page
parent: Installation
nav_order: 1.1
---

# Download the files
HaCasa is installed through HACS as a custom Dashboard repository.

## Verify Prerequisites

Ensure you have the following:

- A running [Home Assistant](https://www.home-assistant.io/) instance.
- Basic knowledge of Home Assistant like changing your `configuration.yaml` file.
- [HACS](https://hacs.xyz) installed.
- Access to your Home Assistant configuration folder.

## Backup Your Home Assistant

1. Navigate to `Settings` > `System` > `Backups`.
2. Create a backup of your Home Assistant instance.
3. Alternatively, [click here](https://my.home-assistant.io/redirect/backup/) to create a backup directly.

**Note:** We are not responsible for any data loss. Always ensure you have a backup before proceeding.

## Install Required Dependencies

Install the following integrations through HACS or manual installation:

- [Button Card](https://github.com/custom-cards/button-card) by RomRider.
- [my-slider-v2](https://github.com/AnthonMS/my-cards) by AnthonMS (part of the `my-cards` integration).
- [Card Mod](https://github.com/thomasloven/lovelace-card-mod) by Thomas Lovén.
- [Mini Graph Card](https://github.com/kalkih/mini-graph-card) by Karl Kihlström.
- [Kiosk Mode](https://github.com/NemesisRE/kiosk-mode) by NemesisRE.
- [Layout Card](https://github.com/thomasloven/lovelace-layout-card) by Thomas Lovén.

## Install HaCasa with HACS

1. Open HACS.
2. Open the three-dot menu and choose **Custom repositories**.
3. Add `https://github.com/digas111/HaCasa` as a **Dashboard** repository.
4. Search for **HaCasa** in HACS and download it.
5. Restart Home Assistant after the download finishes.

HACS installs HaCasa to this folder:

```markdown
www/
└── community/
    └── HaCasa/
```

## Verify File Structure

Ensure your HACS-managed file structure matches the following:

```markdown
www/community/HaCasa/
├── HaCasa.js
├── dashboard/
│   └── HaCasa/
│       ├── templates/
│       ├── views/
│       └── main.yaml
├── images/
│   ├── music/
│   └── weather/
└── themes/
    └── HaCasa/
```

## Proceed to Configuration

Once the files are in place, proceed to the [configuration guide]({{ '/docs/installation/configuration.html' | relative_url }}) to set up your dashboard.
