---
title: Toggle Graph Card
layout: page
parent: Cards
---

# Toggle Graph Card

The `hc_toggle_graph_card` extends `hc_graph_card` by linking a sensor graph to a second entity that can be toggled from the card.

## Usage

```yaml
  - type: custom:button-card
    template: hc_toggle_graph_card
    entity: <your sensor entity>
    name: Heater
    variables:
      toggle_entity: <your switch entity>
      active_color: var(--color-orange)
```

**Remember to take care of indentation**

## Variable / entry

| Variable | Default | Required | Example |
|:----------|:---------|:----------|:------------|
| <span class="entry-type-ha"></span> entity | | **Yes** | sensor.heater_power |
| <span class="entry-type-ha"></span> name | friendly name | No | Heater |
| <span class="entry-type-hacasa"></span> toggle_entity | | **Yes** | switch.heater |
| <span class="entry-type-hacasa"></span> active_color | var(--primary-color) | No | var(--color-orange) |
| <span class="entry-type-hacasa"></span> active_content_color | white | No | white |
| <span class="entry-type-hacasa"></span> active_icon_background | var(--opacity-contrast-100) | No | var(--opacity-contrast-100) |
| <span class="entry-type-hacasa"></span> inactive_background | var(--ha-card-background) | No | var(--ha-card-background) |
| <span class="entry-type-hacasa"></span> inactive_name_color | var(--subtext-color) | No | var(--subtext-color) |
| <span class="entry-type-hacasa"></span> inactive_state_color | var(--primary-text-color) | No | var(--primary-text-color) |
| <span class="entry-type-hacasa"></span> inactive_icon_color | var(--icon-color-default) | No | var(--icon-color-default) |
| <span class="entry-type-hacasa"></span> inactive_icon_background | var(--background-icon-color-default) | No | var(--background-icon-color-default) |
| <span class="entry-type-hacasa"></span> show_graph_fill | true | No | true |
| <span class="entry-type-hacasa"></span> show_graph_line | true | No | true |
| <span class="entry-type-hacasa"></span> show_icon | true | No | true |

## More info

This card inherits graph behavior from `hc_graph_card`, including the Mini Graph Card dependency.
