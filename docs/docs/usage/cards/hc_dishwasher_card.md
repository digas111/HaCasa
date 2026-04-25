---
title: Dishwasher Card
layout: page
parent: Cards
---

# Dishwasher Card

The `hc_dishwasher_card` is used to show dishwasher operation state, program progress, remaining time, active program icon, and salt or rinse-aid attention chips.

## Usage

```yaml
  - type: custom:button-card
    template: hc_dishwasher_card
    entity: <your dishwasher operation state sensor>
    name: Dishwasher
    variables:
      progress_entity: <your progress sensor>
      salt_entity: <your salt warning sensor>
      rinse_aid_entity: <your rinse aid warning sensor>
      remaining_time_entity: <your remaining time sensor>
      active_program_entity: <your active program select>
```

**Remember to take care of indentation**

## Variable / entry

| Variable | Default | Required | Example |
|:----------|:---------|:----------|:------------|
| <span class="entry-type-ha"></span> entity | sensor.bd_loica_operation_state | **Yes** | sensor.dishwasher_operation_state |
| <span class="entry-type-ha"></span> name | Maquina Loica | No | Dishwasher |
| <span class="entry-type-hacasa"></span> progress_entity | sensor.bd_loica_program_progress | No | sensor.dishwasher_program_progress |
| <span class="entry-type-hacasa"></span> salt_entity | sensor.bd_loica_quase_sem_sal | No | sensor.dishwasher_salt_nearly_empty |
| <span class="entry-type-hacasa"></span> rinse_aid_entity | sensor.bd_loica_rinse_aid_nearly_empty | No | sensor.dishwasher_rinse_aid_nearly_empty |
| <span class="entry-type-hacasa"></span> remaining_time_entity | sensor.bd_loica_remaining_program_time | No | sensor.dishwasher_remaining_program_time |
| <span class="entry-type-hacasa"></span> active_program_entity | select.bd_loica_active_program | No | select.dishwasher_active_program |

## More info

The operation state supports values such as `inactive`, `ready`, `run`, `pause`, `delayedstart`, `actionrequired`, `finished`, `error`, and `aborting`. The progress sensor should return a number from 0 to 100.
