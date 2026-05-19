# Office Tracker for Home Assistant

A custom integration to automatically track your office days based on location, track vacation and public holidays, and compute a rolling 12-week and quarterly average to ensure you are meeting your Office requirements.

![Icon](https://github.com/otw/office-tracker/raw/main/custom_components/office_tracker/icon.png)

## Features
- **UI Configuration Wizard**: Easily select your person and zone entities right from the Home Assistant interface. No YAML required!
- **Automatic Tracking**: Uses your `person` entity and Home Assistant Zones to automatically log office days.
- **Configurable Cumulative Timers**: Set a `required_hours` (e.g. 4.0 hours). The integration tracks cumulative time spent in the office zone during the day, pausing if you leave for lunch, and credits you the moment you hit the threshold.
- **Live Status Sensor**: View a real-time sensor (`sensor.office_time_in_office_today`) that tracks how many hours you have been in the office today.
- **Holiday Tracking**: Pick a public holiday calendar during setup. If the calendar is active at midnight, it credits you with a "Holiday", protecting your rolling averages.
- **Dedicated Calendar**: Exposes a full Home Assistant Calendar entity (`calendar.office_tracker`) plotting all your past Office Days, Vacation Days, and Holidays.
- **Dynamic Targets**: Set your required days per week in the setup UI. The sensors expose these dynamically as attributes for your Lovelace cards and Automations.

---

## Installation Instructions

### Step 1: Create Your Office Zone
Home Assistant needs to know where your office is located on a map.
1. Go to **Settings -> Areas, Labels & Zones**.
2. Click the **Zones** tab at the top.
3. Click the **+ Add Zone** button in the bottom right corner.
4. Name it something like "Downtown Office".
5. Click on the map to drop the pin at your office building, and drag the circle to cover the area.
6. Click **Create**.

### Step 2: Ensure Your Person Entity is Linked
Home Assistant needs to know which phone/device to track.
1. Go to **Settings -> People**.
2. Click on your name.
3. Ensure that your mobile phone (with the Home Assistant Companion App installed) is selected under the **"Track device"** section.

### Step 3: Install the Integration
1. Install this integration via [HACS](https://hacs.xyz/) (Home Assistant Community Store) by adding this repository as a Custom Repository (Category: Integration).
2. **Restart Home Assistant** entirely.
3. Go to **Settings -> Devices & Services**.
4. Click **Add Integration** in the bottom right corner.
5. Search for **Office Tracker**.
6. A wizard will pop up. Select your Person entity, the Office Zone you just created, and your required weekly targets.

### Step 4: Add the UI Dashboard Popups (Optional but Recommended)
Want beautiful calendar popups on your dashboard to manually log a week of vacation? We use native Home Assistant Scripts to achieve this!
1. Go to **Settings -> Automations & Scenes -> Scripts**.
2. Click **+ Add Script** -> **Edit in YAML**.
3. Delete the empty code, and paste in the "Log Vacation Range" script from our [scripts_example.yaml](https://github.com/otw/office-tracker/blob/main/scripts_example.yaml). **Note:** Remove the top-level ID (e.g., `log_office_vacation_range:`) and start copying from the `alias:` line!
4. Save the script. Repeat this process for the "Log Office Range" script.
5. Edit your Lovelace dashboard and copy the card configuration from [ui_lovelace_example.yaml](https://github.com/otw/office-tracker/blob/main/ui_lovelace_example.yaml). Tapping those buttons will now natively pop up the calendars!

### Step 5: Add an Automation (Optional)
Want to be notified if you are falling behind your office requirements?
1. Go to **Settings -> Automations & Scenes -> Automations**.
2. Click **+ Create Automation** -> **Edit in YAML**.
3. Copy the contents of the [automations_example.yaml](https://github.com/otw/office-tracker/blob/main/automations_example.yaml) into the editor.
4. Save. You will now get a warning notification on your phone at 6:00 PM on weekdays if your 12-week rolling average falls below your target!
