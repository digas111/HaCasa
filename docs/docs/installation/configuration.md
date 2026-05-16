---
title: Configuration
layout: page
parent: Installation
nav_order: 1.2
---

# Configure HaCasa

After installing HaCasa with HACS, add the dashboard, themes, icons, and resources to `configuration.yaml`.

## Step 1: Open `configuration.yaml`

Open the `configuration.yaml` file in your Home Assistant configuration folder.

If you use the File editor add-on, Studio Code Server add-on, Samba share, SSH, or another editor, use the method you normally use to edit Home Assistant YAML files.

## Step 2: Load HaCasa Themes and Icons

Add this block to `configuration.yaml`. If you already have a `frontend:` block, merge the `themes` and `extra_module_url` lines into your existing block instead of creating a second `frontend:` block.

```yaml
frontend:
  themes: !include_dir_merge_named www/community/HaCasa/themes
  extra_module_url:
    - /hacsfiles/HaCasa/HaCasa.js
```

This loads the HaCasa themes and the bundled `hacasa:` icon set.

## Step 3: Add the HaCasa Dashboard

Add this block to `configuration.yaml`. If you already have a `lovelace:` block, merge the `resources` and `dashboards` entries into your existing block instead of creating a second `lovelace:` block.

```yaml
lovelace:
  mode: "storage"
  resources:
    - url: "/hacsfiles/HaCasa/HaCasa.js"
      type: "module"
    - url: "/hacsfiles/button-card/button-card.js"
      type: "module"
    - url: "/hacsfiles/my-cards/my-cards.js"
      type: "module"
    - url: "/hacsfiles/kiosk-mode/kiosk-mode.js"
      type: "module"
    - url: "/hacsfiles/lovelace-card-mod/card-mod.js"
      type: "module"
    - url: "/hacsfiles/mini-graph-card/mini-graph-card-bundle.js"
      type: "module"
    - url: "/hacsfiles/lovelace-layout-card/layout-card.js"
      type: "module"
    - url: "https://fonts.googleapis.com/css2?family=Montserrat:wght@100;200;300;400;500;600;700;800;900"
      type: "css"
  dashboards:
    hacasa-dashboard:
      mode: "yaml"
      title: HaCasa
      icon: mdi:home
      show_in_sidebar: true
      filename: "www/community/HaCasa/dashboard/HaCasa/main.yaml"
```

This keeps your normal Home Assistant dashboards in storage mode and adds HaCasa as a separate YAML dashboard in the sidebar.

## Step 4: Save and Restart Home Assistant

1. Save `configuration.yaml`.
2. Restart Home Assistant.
3. Wait until Home Assistant is fully started again.

## Step 5: Select a HaCasa Theme

1. Open your Home Assistant profile settings.
2. Find the **Theme** selector.
3. Select **HaCasa Gold** or **HaCasa Peach**.
4. Save your profile settings.

You can open the profile page directly with [this Home Assistant link](https://my.home-assistant.io/redirect/profile).

## Step 6: Create Your First View

HaCasa loads dashboard views from:

```text
www/community/HaCasa/dashboard/HaCasa/views
```

Create a file named:

```text
00-default_view.yaml
```

Add this starter view and replace the weather entity with your own:

```yaml
title: Home
path: "home"
icon: hacasa:house-fill
cards:
  - type: vertical-stack
    cards:
      - type: custom:button-card
        template: hc_header_card
        entity: weather.home
      - type: custom:button-card
        template: hc_title_card
        name: "Welcome Home"
        label: "What are you up to"
```

## Step 7: Open the Dashboard

1. Open Home Assistant.
2. Select **HaCasa** in the sidebar.
3. If the dashboard was already open before you edited files, open the three-dot menu in the top-right corner and select **Refresh**.

If the dashboard does not appear, check that `configuration.yaml` uses this exact filename:

```yaml
filename: "www/community/HaCasa/dashboard/HaCasa/main.yaml"
```

If icons or weather images do not load, check that this resource exists in `lovelace.resources`:

```yaml
- url: "/hacsfiles/HaCasa/HaCasa.js"
  type: "module"
```
