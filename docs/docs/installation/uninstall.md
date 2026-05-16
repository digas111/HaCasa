---
title: Uninstall
layout: page
parent: Installation
nav_order: 1.5
---

# Uninstall

To uninstall HaCasa cleanly, remove the HACS package and then remove the YAML configuration that points Home Assistant at the package.

1. Open HACS.
2. Open the HaCasa repository page.
3. Choose **Remove**. HACS removes the `www/community/HaCasa` folder.
4. In your `configuration.yaml` file, remove this dashboard entry:

   ```yaml
   hacasa-dashboard:
     mode: "yaml"
     title: HaCasa
     icon: mdi:home
     show_in_sidebar: true
     filename: "www/community/HaCasa/dashboard/HaCasa/main.yaml"
   ```

5. Remove the HaCasa module and theme references:

   ```yaml
   frontend:
     themes: !include_dir_merge_named www/community/HaCasa/themes
     extra_module_url:
       - /hacsfiles/HaCasa/HaCasa.js
   ```

6. Remove the HaCasa resource entry from `lovelace.resources`:

   ```yaml
   - url: "/hacsfiles/HaCasa/HaCasa.js"
     type: "module"
   ```

7. If you want to remove the whole YAML dashboard block, make sure this is gone too:

   ```yaml
   lovelace:
     mode: "storage"
     resources:
       ...
     dashboards:
       hacasa-dashboard:
           mode: "yaml"
           title: HaCasa
           icon: mdi:home
           show_in_sidebar: true
           filename: "www/community/HaCasa/dashboard/HaCasa/main.yaml"
   ```

8. Restart Home Assistant.
