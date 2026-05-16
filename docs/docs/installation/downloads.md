---
title: Downloads
layout: page
parent: Installation
nav_order: 1.1
---

# Install with HACS

HaCasa is installed through HACS as a custom **Dashboard** repository. HACS downloads and manages the HaCasa files, but you still need to add the dashboard configuration in the next step.

## Before You Start

Make sure you have:

- A running [Home Assistant](https://www.home-assistant.io/) instance.
- [HACS](https://hacs.xyz) installed and visible in the Home Assistant sidebar.
- Access to your Home Assistant configuration folder, where `configuration.yaml` is located.
- Permission to restart Home Assistant.

## Step 1: Back Up Home Assistant

1. In Home Assistant, go to `Settings` > `System` > `Backups`.
2. Create a new backup before changing files.
3. You can also open the backup page directly with [this Home Assistant link](https://my.home-assistant.io/redirect/backup/).

**Note:** Always create a backup before installing custom dashboards or editing `configuration.yaml`.

## Step 2: Install Required Dashboard Dependencies

HaCasa depends on these dashboard cards and modules. Install them in HACS before installing HaCasa:

1. Open HACS from the Home Assistant sidebar.
2. Search for each dependency below.
3. Open the dependency page.
4. Select **Download**.
5. Repeat until all dependencies are installed.

Required dependencies:

- [Button Card](https://github.com/custom-cards/button-card) by RomRider.
- [my-slider-v2](https://github.com/AnthonMS/my-cards) by AnthonMS. This is part of the `my-cards` repository.
- [Card Mod](https://github.com/thomasloven/lovelace-card-mod) by Thomas Lovén.
- [Mini Graph Card](https://github.com/kalkih/mini-graph-card) by Karl Kihlström.
- [Kiosk Mode](https://github.com/NemesisRE/kiosk-mode) by NemesisRE.
- [Layout Card](https://github.com/thomasloven/lovelace-layout-card) by Thomas Lovén.

## Step 3: Add HaCasa as a Custom HACS Repository

1. Open HACS from the Home Assistant sidebar.
2. Select the three-dot menu in the top-right corner.
3. Select **Custom repositories**.
4. In the **Repository** field, enter:

   ```text
   https://github.com/digas111/HaCasa
   ```

5. In the **Category** or **Type** field, select **Dashboard**.
6. Select **Add**.
7. Close the custom repositories dialog.

If HACS does not accept the repository, confirm that the category is set to **Dashboard**.

## Step 4: Download HaCasa

1. In HACS, search for **HaCasa**.
2. Open the HaCasa repository page.
3. Select **Download**.
4. Keep the newest version selected unless you need a specific older release.
5. Confirm the download.
6. Wait until HACS finishes downloading the package.

## Step 5: Restart Home Assistant

1. Go to `Settings` > `System` > `Restart Home Assistant`.
2. Restart Home Assistant.
3. After Home Assistant starts again, continue with the configuration page.

## Step 6: Verify the Installed Files

HACS installs HaCasa under your Home Assistant configuration folder:

```markdown
www/
└── community/
    └── HaCasa/
```

The installed folder should contain:

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

## Next Step

HACS has now installed the files. Continue to the [configuration guide]({{ '/docs/installation/configuration.html' | relative_url }}) to add the HaCasa dashboard to Home Assistant.
