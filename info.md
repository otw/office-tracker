# Return To Office (RTO) Tracker

A highly polished, production-tier Home Assistant integration to track your Return To Office compliance!

![Icon](https://github.com/otw/rto-tracker/raw/main/custom_components/rto_tracker/icon.png)

## Why use this?
If your company mandates "2 days a week" over a rolling 12-week period, it can be extremely difficult to manually track if you are compliant, especially factoring in vacations and public holidays. This integration completely automates it.

## Features:
- **Native UI Setup**: No YAML needed! Complete your setup directly through Home Assistant's *Devices & Services* wizard.
- **Smart Tracking**: Provide an office zone and a required daily duration (e.g., `4.0` hours). It tracks your cumulative time and automatically credits you when you hit the threshold.
- **Public Holidays & Vacations**: Automatically links to Home Assistant calendars to credit you for public holidays.
- **Dedicated Calendar View**: Adds a custom Home Assistant Calendar entity so you can visually see all your past office and vacation days.
- **Live Status Sensor**: Watch your hours tick up in real-time on your dashboard while you are in the office.

## Getting Started
After installing this repository, simply restart Home Assistant, go to **Settings -> Devices & Services**, click **Add Integration**, and search for "RTO Tracker" to launch the wizard!
