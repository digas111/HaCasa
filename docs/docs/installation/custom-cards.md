---
title: Custom Cards
layout: page
parent: Installation
nav_order: 1.4
---
# Custom Cards

HaCasa includes internal templates and custom templates. Internal templates are the standard cards shipped with the dashboard. Custom templates are optional cards in `www/community/HaCasa/dashboard/HaCasa/templates/custom_templates` that you can use, copy, or adapt for more specific devices.

## Included custom templates

The following custom templates are included:

| Template | Purpose |
|:---------|:--------|
| `custom_hc_cover_card` | Cover, blind, or shutter control with a position slider. |
| `hc_battery_card` | Battery sensor display with color thresholds. |
| `hc_climate_mode_card` | Climate card variant for mode selector setups. |
| `hc_dishwasher_card` | Dishwasher status, progress, remaining time, and maintenance indicators. |
| `hc_number_card` | `input_number` display with increment and decrement controls. |
| `hc_toggle_graph_card` | Sensor graph card that toggles a related entity. |
| `hc_vacuum_card` | Robot vacuum controls with segment cleaning buttons. |
| `hc_washing_machine_card` | Washing machine state and elapsed runtime display. |

## Using a custom template

Use custom templates the same way as the regular HaCasa cards:

```yaml
  - type: custom:button-card
    template: hc_battery_card
    entity: sensor.front_door_battery
    name: Front Door
```

The dashboard includes all templates from the `templates` directory through `button_card_templates`, so no extra include line is needed when the files are copied into the expected folder.

## Dependencies

Custom templates can rely on the same frontend dependencies as the rest of HaCasa:

- `custom:button-card`
- `custom:my-slider-v2` for `custom_hc_cover_card`
- Mini Graph Card for `hc_toggle_graph_card`
- Card Mod where inherited graph styling is used

Some cards also expect helper entities from your Home Assistant installation. For example, `hc_dishwasher_card` uses variables for progress, remaining time, salt, rinse aid, and active program entities. Check each card page under Usage > Cards for the available variables.
