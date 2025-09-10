# Climate Setback Controller

A Home Assistant custom component that automatically controls climate devices based on schedule devices, implementing temperature setback functionality.

## Features

- **Automatic Setback Control**: Automatically switches between normal and setback temperatures based on schedule device state
- **Manual Override**: Services to manually enable/disable setback mode
- **Configurable Temperatures**: Set custom normal and setback temperatures
- **Schedule Integration**: Works with any Home Assistant schedule entity
- **Climate Device Support**: Compatible with any Home Assistant climate entity

## Installation

### Method 1: HACS (Recommended)

1. Add this repository to HACS as a custom repository
2. Install "Climate Setback Controller" from HACS
3. Restart Home Assistant

### Method 2: Manual Installation

1. Copy the `custom_components/climate_setback` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Add the integration through the UI

## Configuration

### Adding the Integration

1. Go to **Settings** > **Devices & Services**
2. Click **Add Integration**
3. Search for "Climate Setback Controller"
4. Configure the following settings:
   - **Name**: A friendly name for your setback controller
   - **Climate Device**: The climate entity to control (e.g., `climate.living_room_thermostat`)
   - **Schedule Device**: The schedule entity that defines when setback should be active
   - **Setback Temperature**: Temperature to set when schedule is active (e.g., 18°C)
   - **Normal Temperature**: Temperature to set when schedule is inactive (e.g., 22°C)

### Example Configuration

```yaml
# Example schedule for weekday setback
schedule:
  weekday_setback:
    name: "Weekday Setback"
    mode: restart
    actions:
      - service: schedule.turn_on
        data:
          entity_id: schedule.weekday_setback
        time: "22:00:00"
      - service: schedule.turn_off
        data:
          entity_id: schedule.weekday_setback
        time: "06:00:00"
```

## Usage

### Automatic Operation

The component automatically:
- Monitors the schedule device state
- Switches to setback temperature when schedule is active
- Returns to normal temperature when schedule is inactive
- Controls the target temperature of the climate device

### Manual Control

You can manually control setback mode using services:

```yaml
# Enable setback mode
service: climate_setback.set_setback
target:
  entity_id: climate_setback.living_room_controller

# Disable setback mode
service: climate_setback.clear_setback
target:
  entity_id: climate_setback.living_room_controller
```

### Automation Examples

```yaml
# Automatically enable setback when leaving home
automation:
  - alias: "Enable Setback When Away"
    trigger:
      - platform: state
        entity_id: person.john
        to: "not_home"
    action:
      - service: climate_setback.set_setback
        target:
          entity_id: climate_setback.living_room_controller

# Automatically disable setback when returning home
automation:
  - alias: "Disable Setback When Home"
    trigger:
      - platform: state
        entity_id: person.john
        to: "home"
    action:
      - service: climate_setback.clear_setback
        target:
          entity_id: climate_setback.living_room_controller
```

## Entity Attributes

The climate setback entity exposes the following attributes:

- `is_setback`: Boolean indicating if setback mode is currently active
- `setback_temperature`: The configured setback temperature
- `normal_temperature`: The configured normal temperature

## Requirements

- Home Assistant 2023.1.0 or later
- A climate entity (thermostat, heat pump, etc.)
- A schedule entity or any entity with on/off state

## Development

This project uses a dev container for development. To get started:

1. Open the project in VS Code
2. Reopen in Dev Container when prompted
3. The container will automatically install Python dependencies

### Project Structure

```
custom_components/climate_setback/
├── __init__.py          # Main integration setup
├── climate.py           # Climate entity implementation
├── config_flow.py       # Configuration flow
├── const.py            # Constants and configuration keys
├── manifest.json       # Integration manifest
├── services.py         # Service implementations
└── services.yaml       # Service definitions
```

## Troubleshooting

### Common Issues

1. **Climate device not responding**: Ensure the climate device is properly configured and accessible
2. **Schedule not triggering**: Check that the schedule device is working correctly
3. **Temperature not changing**: Verify that the climate device supports temperature control

### Debugging

Enable debug logging by adding this to your `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.climate_setback: debug
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
