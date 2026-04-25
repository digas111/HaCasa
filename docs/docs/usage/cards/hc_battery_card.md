---
title: Battery Card
layout: page
parent: Cards
---

# Battery Card

The `hc_battery_card` is used to show battery percentages. It changes color based on the numeric state: green from 80 and higher, yellow from 20 to 79, and red below 20.

## Usage

```yaml
  - type: custom:button-card
    template: hc_battery_card
    entity: <your battery sensor>
    name: Front Door Sensor
    variables:
      on_icon: mdi:battery
```

**Remember to take care of indentation**

## Variable / entry

| Variable | Default | Required | Example |
|:----------|:---------|:----------|:------------|
| <span class="entry-type-ha"></span> entity | | **Yes** | sensor.front_door_battery |
| <span class="entry-type-ha"></span> name | friendly name | No | Front Door Sensor |
| <span class="entry-type-hacasa"></span> on_icon | mdi:battery | No | mdi:battery-70 |
