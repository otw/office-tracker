# Return To Office (RTO) Tracker for Home Assistant

A custom integration to automatically track your office days based on location, track vacation days, and compute a rolling 12-week and quarterly average to ensure you are meeting your RTO requirements.

## Features
- **UI Configuration Wizard**: Easily select your person and zone entities right from the Home Assistant interface. No YAML required!
- **Automatic Tracking**: Uses your `person` entity and Home Assistant Zones to automatically log office days.
- **Persistent Data**: Survives Home Assistant reboots natively.
- **Rolling Averages**: Computes your "12-Week Rolling" and "Current Quarter" counts.
- **Services**: Manually add or remove office and vacation days.

## Installation
1. Install via [HACS](https://hacs.xyz/) by adding this repository as a Custom Repository (Category: Integration).
2. Restart Home Assistant.
3. Go to **Settings** -> **Devices & Services**.
4. Click **Add Integration** in the bottom right corner.
5. Search for **RTO Tracker** and follow the on-screen instructions to select your entities.
