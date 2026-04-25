---
title: Vacuum Card
layout: page
parent: Cards
---

# Vacuum Card

The `hc_vacuum_card` is used to control a robot vacuum. It includes return-to-base, pause, start, and three segment cleaning buttons.

## Usage

```yaml
  - type: custom:button-card
    template: hc_vacuum_card
    entity: <your vacuum entity>
    variables:
      action_1:
        icon: mdi:door
        segment: 21
      action_2:
        icon: mdi:sofa
        segment: 22
      action_3:
        icon: mdi:bed
        segment: 23
```

**Remember to take care of indentation**

## Variable / entry

| Variable | Default | Required | Example |
|:----------|:---------|:----------|:------------|
| <span class="entry-type-ha"></span> entity | | **Yes** | vacuum.downstairs |
| <span class="entry-type-hacasa"></span> icon | mdi:robot-vacuum | No | mdi:robot-vacuum |
| <span class="entry-type-hacasa"></span> action_1.icon | mdi:door | No | mdi:silverware-fork-knife |
| <span class="entry-type-hacasa"></span> action_1.on_action | vacuum.send_command | No | vacuum.send_command |
| <span class="entry-type-hacasa"></span> action_1.segment | 21 | No | 16 |
| <span class="entry-type-hacasa"></span> action_2.icon | mdi:sofa | No | mdi:sofa |
| <span class="entry-type-hacasa"></span> action_2.on_action | vacuum.send_command | No | vacuum.send_command |
| <span class="entry-type-hacasa"></span> action_2.segment | 22 | No | 17 |
| <span class="entry-type-hacasa"></span> action_3.icon | mdi:bed | No | mdi:bed |
| <span class="entry-type-hacasa"></span> action_3.on_action | vacuum.send_command | No | vacuum.send_command |
| <span class="entry-type-hacasa"></span> action_3.segment | 23 | No | 18 |

## More info

The room buttons send the `app_segment_clean` command. Segment IDs are integration-specific, so update them to match your vacuum map.
