---
title: Climate Mode Card
layout: page
parent: Cards
---

# Climate Mode Card

The `hc_climate_mode_card` extends `hc_climate_card` and is reserved for climate setups that need a mode selector hash.

## Usage

```yaml
  - type: custom:button-card
    template: hc_climate_mode_card
    entity: <your climate entity>
    variables:
      mode_selector_hash: "#mode-selector"
```

**Remember to take care of indentation**

## Variable / entry

| Variable | Default | Required | Example |
|:----------|:---------|:----------|:------------|
| <span class="entry-type-ha"></span> entity | | **Yes** | climate.living_room |
| <span class="entry-type-hacasa"></span> mode_selector_hash | | No | "#mode-selector" |

## More info

This template inherits the behavior and requirements from `hc_climate_card`.
