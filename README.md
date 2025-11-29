[![GitHub Release][releases-shield]][releases]
[![Total downloads][total-downloads-shield]][total-downloads]
[![Latest release downloads][latest-release-downloads-shield]][latest-release-downloads]

<p align="right">
<img width="250" alt="Logo" src="https://raw.githubusercontent.com/toringer/home-assistant-thermostat-setback/master/assets/icon.png">
</p>

# Thermostat Setback Controller

**Simple, automated thermostat setback control without complex automation setup.**

Stop wrestling with complex Home Assistant automations for your thermostat! This controller makes temperature setback management effortless - just set it up once and it handles everything automatically.

## Why Choose This Controller?

- **No Complex Automation Required**: Forget about writing YAML automations or dealing with complex logic
- **One-Time Setup**: Configure once through the UI and it works forever
- **Smart & Automatic**: Seamlessly switches between normal and setback temperatures based on your schedule
- **Manual Control When Needed**: Override anytime with simple controls
- **Skip Setback Feature**: Temporarily skip the next setback cycle when you need normal temperature
- **External Integration**: Works with any binary sensor or switch for additional control

<p align="center">
<img width="350" alt="Thermostat Setback Controller" src="https://raw.githubusercontent.com/toringer/home-assistant-thermostat-setback/master/assets/device.png">
</p>


## Sensors Created

The integration creates two sensors for monitoring:

### 1. Setback Status Sensor
- **Name**: "Setback Status" (or your custom name)
- **Value**: `on` when setback is active, `off` when normal temperature is active
- **Attributes**:
  - `climate_device`: The controlled thermostat entity
  - `schedule_device`: The schedule helper entity
  - `binary_input_device`: Optional binary input for manual control

### 2. Recovery Time Sensor
Tracks how long it takes for temperature to reach normal after setback ends

- **Name**: "Recovery Time"
- **Value**: Time in seconds it took for the last recovery from setback to normal temperature
- **Unit**: Seconds (s)
- **Attributes**:
  - `is_recovering`: `true` when currently recovering from setback, `false` otherwise


## Controls Created

The integration creates three switches for manual control:

### 1. Force Setback Switch
Manually override to force setback mode on or off, regardless of schedule or other conditions.

- **Name**: "Force Setback"
- **State**: `on` when forced setback is active, `off` when not forced
- **Usage**: Turn on to manually enable setback, turn off to return to automatic control

### 2. Controller Active Switch
Enable or disable the entire controller.

- **Name**: "Controller Active"
- **State**: `on` when controller is active, `off` when disabled
- **Usage**: Turn off to completely disable temperature control, turn on to re-enable

### 3. Skip Setback Switch
Skip the next scheduled setback cycle.

- **Name**: "Skip Setback"
- **State**: `on` when skip is active, `off` when not skipping
- **Usage**:
  - Turn on to skip the next setback cycle when your schedule becomes active
  - If currently in setback, turning this on will immediately return to normal temperature
  - The flag automatically resets after the next setback cycle is skipped
  - Useful for temporarily preventing setback when you know you'll be home or need normal temperature


## Installation

### Method 1: HACS (Recommended)

1. Add this repository to HACS as a custom repository
2. Install "Thermostat Setback Controller" from HACS
3. Restart Home Assistant

### Method 2: Manual Installation

1. Copy the `custom_components/thermostat_setback` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Add the integration through the UI

## Quick Setup (2 Minutes!)

### Step 1: Add the Integration

1. Go to **Settings** > **Devices & Services**
2. Click **Add Integration**
3. Search for "Thermostat Setback Controller"
4. Fill in these simple settings:
   - **Name**: Give it a friendly name (e.g., "Living Room Setback")
   - **Climate Device**: Pick your thermostat (e.g., `climate.living_room_thermostat`)
   - **Schedule Device**: Choose your schedule helper (defines when setback is active)
   - **Forced Setback Monitoring Sensor**: Optional - use any switch/sensor for manual control forced setback

### Step 2: That's It!

The controller immediately starts working:
- ✅ **Automatically** switches to setback temperature when your schedule is active
- ✅ **Automatically** returns to normal temperature when schedule is inactive
- ✅ **No YAML needed** - everything is handled through the UI
- ✅ **Works forever** - set it and forget it!


## Development

This project uses a dev container for development. To get started:

1. Open the project in VS Code
2. Reopen in Dev Container when prompted
3. The container will automatically install Python dependencies

### Project Structure

```
custom_components/thermostat_setback/
├── __init__.py          # Main integration setup
├── climate.py           # Climate entity implementation
├── config_flow.py       # Configuration flow
├── const.py            # Constants and configuration keys
├── manifest.json       # Integration manifest
├── services.py         # Service implementations
└── services.yaml       # Service definitions
```

## Troubleshooting

### Debugging

Enable debug logging by adding this to your `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.thermostat_setback: debug
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue on the GitHub repository.


[releases-shield]: https://img.shields.io/github/v/release/toringer/home-assistant-thermostat-setback?style=flat-square
[releases]: https://github.com/toringer/home-assistant-thermostat-setback/releases
[total-downloads-shield]: https://img.shields.io/github/downloads/toringer/home-assistant-thermostat-setback/total?style=flat-square
[total-downloads]: https://github.com/toringer/home-assistant-thermostat-setback
[latest-release-downloads-shield]: https://img.shields.io/github/downloads/toringer/home-assistant-thermostat-setback/latest/total?style=flat-square
[latest-release-downloads]: https://github.com/toringer/home-assistant-thermostat-setback