---
title: Washing Machine Card
layout: page
parent: Cards
---

# Washing Machine Card

The `hc_washing_machine_card` is used to show a washing machine binary sensor state and the elapsed runtime while the entity is `on`.

## Usage

```yaml
  - type: custom:button-card
    template: hc_washing_machine_card
    entity: <your washing machine binary sensor>
    name: Washing Machine
```

**Remember to take care of indentation**

## Variable / entry

| Variable | Default | Required | Example |
|:----------|:---------|:----------|:------------|
| <span class="entry-type-ha"></span> entity | binary_sensor.maquina_roupa | **Yes** | binary_sensor.washing_machine |
| <span class="entry-type-ha"></span> name | Maquina Roupa | No | Washing Machine |

## More info

The timer uses the entity `last_changed` value, so it resets when the binary sensor changes state.
