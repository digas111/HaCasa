---
title: Installation
layout: page
nav_order: 1
---

# Installation

HaCasa can be installed with HACS as a custom Dashboard repository. This is the recommended installation method because HACS keeps the dashboard files in one managed folder and can remove those files again when you uninstall it.
{: .fs-6 .fw-300 }

HaCasa still relies on YAML configuration. Home Assistant's UI editor does not yet support the include directives used by HaCasa and many other advanced dashboards, so you still need to edit `configuration.yaml`.

HACS installs the files, but you add the Lovelace dashboard entry and theme include yourself.

## But can I add it to the raw config?
Yes but please... **don't**. Home Assistant only allows you to include files in yaml-mode and because HaCasa (and many other dashboards) make use of this function we can only support the yaml mode.

There is a feature request at the Home Assistant forum, if you’d like to see this function available in UI-mode, too, you might want to give your vote in [this thread](https://community.home-assistant.io/t/ability-to-use-include-directives-in-ui-editor/336167?u=paddy0174).
