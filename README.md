# Return To Office (RTO) Tracker for Home Assistant

A custom integration to automatically track your office days based on location, track vacation days, and compute a rolling 12-week and quarterly average to ensure you are meeting your RTO requirements.

## Features
- **Automatic Tracking**: Uses your `person` entity and Home Assistant Zones to automatically log office days.
- **Persistent Data**: Survives Home Assistant reboots natively.
- **Rolling Averages**: Computes your "12-Week Rolling" and "Current Quarter" counts.
- **Services**: Manually add or remove office and vacation days.

## Installation
1. Install via [HACS](https://hacs.xyz/) by adding this repository as a Custom Repository (Category: Integration).
2. Add the following to your `configuration.yaml`:

```yaml
rto_tracker:
  entity_id: person.your_person
  office_zones:
    - zone.office_1
    - zone.office_2
```
3. Restart Home Assistant.
