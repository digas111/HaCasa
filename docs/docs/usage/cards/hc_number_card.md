---
title: Number Card
layout: page
parent: Cards
---

# Number Card

The `hc_number_card` is used to show and adjust an `input_number` with increment and decrement buttons.

## Usage

```yaml
  - type: custom:button-card
    template: hc_number_card
    entity: <your input number entity>
    name: Charge Limit
```

**Remember to take care of indentation**

## Variable / entry

| Variable | Default | Required | Example |
|:----------|:---------|:----------|:------------|
| <span class="entry-type-ha"></span> entity | | **Yes** | input_number.charge_limit |
| <span class="entry-type-ha"></span> name | friendly name | No | Charge Limit |

## More info

The card reads the entity `min`, `max`, and `unit_of_measurement` attributes. The up and down buttons disable themselves when the current value reaches the configured limits.
