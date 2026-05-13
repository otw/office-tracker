# Return To Office (RTO) Tracker for Home Assistant

A custom integration to automatically track your office days based on location, track vacation and public holidays, and compute a rolling 12-week and quarterly average to ensure you are meeting your RTO requirements.

![Icon](https://github.com/otw/rto-tracker/raw/main/custom_components/rto_tracker/icon.png)

## v2.0 Features
- **UI Configuration Wizard**: Easily select your person and zone entities right from the Home Assistant interface. No YAML required!
- **Automatic Tracking**: Uses your `person` entity and Home Assistant Zones to automatically log office days.
- **Configurable Cumulative Timers**: Set a `required_hours` (e.g. 4.0 hours). The integration tracks cumulative time spent in the office zone during the day, pausing if you leave for lunch, and credits you the moment you hit the threshold.
- **Live Status Sensor**: View a real-time sensor (`sensor.rto_time_in_office_today`) that tracks how many hours you have been in the office today.
- **Holiday Tracking**: Pick a public holiday calendar during setup. If the calendar is active at midnight, it credits you with a "Holiday", protecting your rolling averages.
- **Dedicated Calendar**: Exposes a full Home Assistant Calendar entity (`calendar.rto_tracker`) plotting all your past Office Days, Vacation Days, and Holidays.
- **Dynamic Targets**: Set your required days per week in the setup UI. The sensors expose these dynamically as attributes for your Lovelace cards and Automations.

## Installation
1. Install via [HACS](https://hacs.xyz/) by adding this repository as a Custom Repository (Category: Integration).
2. Restart Home Assistant.
3. Go to **Settings** -> **Devices & Services**.
4. Click **Add Integration** in the bottom right corner.
5. Search for **RTO Tracker** and follow the on-screen instructions to select your entities.

## Updating from 1.x
Because v2.0 introduces new configuration schema (Targets and Holidays), you must remove the existing RTO Tracker from the `Settings -> Devices & Services` page and click "Add Integration" to re-add it. Your historical data will be preserved automatically!
