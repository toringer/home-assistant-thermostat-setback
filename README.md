[![GitHub Release][releases-shield]][releases]
[![Total downloads][total-downloads-shield]][total-downloads]
[![Latest release downloads][latest-release-downloads-shield]][latest-release-downloads]

<p align="right">
<img width="250" alt="Logo" src="https://raw.githubusercontent.com/toringer/home-assistant-thermostat-setback/master/assets/icon.png">
</p>

# Thermostat Setback Controller

A thermostat setback controller for climate devices in Home Assistant.

## Features

- **Automatic Setback Control**: Automatically switches between normal and setback temperatures based on a schedule helper device
- **Manual Override**: Force setback using a manual override.
- **External Override**: Activate forced setback mode by monitoring a binary sensor or switch entity

<p align="right">
<img width="250" alt="Thermostat Setback Controller" src="https://raw.githubusercontent.com/toringer/home-assistant-thermostat-setback/master/assets/device.png">
</p>


## Installation

### Method 1: HACS (Recommended)

1. Add this repository to HACS as a custom repository
2. Install "Thermostat Setback Controller" from HACS
3. Restart Home Assistant

### Method 2: Manual Installation

1. Copy the `custom_components/thermostat_setback` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Add the integration through the UI

## Configuration

### Adding the Integration

1. Go to **Settings** > **Devices & Services**
2. Click **Add Integration**
3. Search for "Thermostat Setback Controller"
4. Configure the following settings:
   - **Name**: A friendly name for your setback controller
   - **Climate Device**: The climate entity to control (e.g., `climate.living_room_thermostat`)
   - **Schedule Device**: The schedule entity that defines when setback should be active
   - **Forced Setback Monitoring Sensor**: Use an another entity to control the forced setback mode



### Automatic Operation

The component automatically:
- Monitors the schedule device state
- Switches to setback temperature when schedule is active
- Returns to normal temperature when schedule is inactive
- Controls the target temperature of the climate device

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