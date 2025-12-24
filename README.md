
# Voltalis Home Assistant Integration

[![Stable][release-badge]][release-link]
[![Integration quality][integration-quality-badge]][integration-quality-link]
[![Active instalations][integration-active-instalations-badge]][integration-active-instalations-link]
[![All downloads][integration-all-downloads-badge]][integration-all-downloads-link]
[![Latest downloads][integration-latest-downloads-badge]][integration-latest-downloads-link]

**Languages** : [English](README.md) | [Français](README.fr.md)




<!-- Latest release -->
[release-badge]: https://img.shields.io/github/v/release/ppaglier/voltalis-homeassistant?label=release&sort=semver&logo=github
[release-link]: https://github.com/ppaglier/voltalis-homeassistant/releases/latest
<!-- Integration quality -->
[integration-quality-badge]: https://img.shields.io/badge/quality-silver-c0c0c0
[integration-quality-link]: https://developers.home-assistant.io/docs/core/integration-quality-scale/#-silver
<!-- Integration active instalations -->
[integration-active-instalations-badge]: https://img.shields.io/badge/dynamic/json?url=https://analytics.home-assistant.io/custom_integrations.json&query=%24.voltalis.total&color=brightgreen&label=active%20instalations&logo=homeassistant
[integration-active-instalations-link]: https://analytics.home-assistant.io/custom_integrations.json
<!-- Integration all downloads -->
[integration-all-downloads-badge]: https://img.shields.io/github/downloads/ppaglier/voltalis-homeassistant/total?&color=blue&logo=github
[integration-all-downloads-link]: https://github.com/ppaglier/voltalis-homeassistant/releases
<!-- Integration latest downloads -->
[integration-latest-downloads-badge]: https://img.shields.io/github/downloads/ppaglier/voltalis-homeassistant/latest/total?&color=blue&logo=homeassistantcommunitystore
[integration-latest-downloads-link]: https://github.com/ppaglier/voltalis-homeassistant/releases/latest
<!-- HACS button -->
[hacs-badge]: https://my.home-assistant.io/badges/hacs_repository.svg
[hacs-link]: https://my.home-assistant.io/redirect/hacs_repository/?owner=ppaglier&repository=voltalis-homeassistant&category=integration



## About Voltalis

Voltalis is a French company that provides smart energy management solutions to help households and businesses reduce electricity consumption and support grid stability. Their innovative technology helps optimize energy usage while maintaining comfort, allowing users to:

- Monitor real-time energy consumption of their heating and water heating devices
- Reduce electricity bills through smart energy management
- Contribute to grid stability and environmental sustainability
- Gain insights into their energy usage patterns

You can learn more about their solutions on their official website: [https://www.voltalis.com](https://www.voltalis.com).

This integration allows you to connect your Voltalis devices to Home Assistant, enabling you to monitor your energy consumption and device connectivity status directly from your Home Assistant dashboard.

## Features

This integration provides comprehensive control and monitoring of your Voltalis devices through multiple entity types:

### Climate Control (for heating devices)
- Full thermostat control with HVAC modes (Off, Heat, Auto)
- Preset modes (Comfort, Eco, Frost Protection, Temperature)
- Target temperature control
- Automatic and manual programming modes
- Advanced service actions for quick boost and timed manual mode

### Sensors
- **Energy Consumption**: Monitor cumulative energy consumption (in Wh)
- **Connection Status**: Check if devices are online and connected
- **Current Mode**: View the active operating mode (Comfort, Eco, Frost Protection, etc.)
- **Programming Type**: See which programming is active (Manual, Default, User, Quick)

### Controls
- **Preset Selector**: Quickly change device mode (Auto, Comfort, Eco, Frost Protection, Temperature, On, Off)

## Installation

### Prerequisites

Before installing this integration, you need:

- A valid Voltalis account (the email and password you use to connect to the Voltalis mobile app or website)
- At least one Voltalis device installed and configured in your home
- Home Assistant 2024.1.0 or newer

### Installation via HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.][hacs-badge]][hacs-link]

<details>
  <summary>Click to show installation instructions</summary>

  1. Make sure you have [HACS](https://hacs.xyz/) installed in your Home Assistant instance
  2. In Home Assistant, go to **HACS** > **Integrations**
  3. Click on the **⋮** menu in the top-right corner and select **Custom repositories**
  4. Add this repository URL: `https://github.com/ppaglier/voltalis-homeassistant`
  5. Set category to **Integration**
  6. Click **Add**
  7. Search for "Voltalis" in HACS and click **Download**
  8. Restart Home Assistant
</details>

### Manual Installation

<details>
  <summary>Click to show manual installation instructions</summary>

  1. Download the latest release from the [releases page](https://github.com/ppaglier/voltalis-homeassistant/releases)
  2. Extract the `custom_components/voltalis` folder from the archive
  3. Copy the `voltalis` folder to your Home Assistant `custom_components` directory:
    - If the `custom_components` directory doesn't exist, create it in your Home Assistant configuration directory (where `configuration.yaml` is located)
    - The final path should be: `<config_dir>/custom_components/voltalis/`
  4. Restart Home Assistant
</details>

## Configuration

### Adding the Integration

<details>
  <summary>Click to configuration instructions</summary>

  1. In Home Assistant, go to **Settings** > **Devices & Services**
  2. Click on the **+ Add Integration** button
  3. Search for "Voltalis" and select it
  4. Enter your Voltalis credentials:
    - **Email address**: The email address associated with your Voltalis account
    - **Password**: Your Voltalis account password
  5. Click **Submit**

  The integration will validate your credentials and automatically discover all your Voltalis devices.
</details>

### Reconfiguration

<details>
  <summary>Click to reconfiguration instructions in case you need to update your credentials</summary>

  1. Go to **Settings** > **Devices & Services**
  2. Find the Voltalis integration
  3. Click on the **⋮** menu and select **Reconfigure**
  4. Enter your new credentials
  5. Click **Submit**
</details>

## Important: Temperature Control Configuration

<details>
  <summary>⚠️ Required Configuration for Temperature Control (Click to expand)</summary>

  ### Prerequisites for Temperature Mode

  Before using the **Temperature preset** or the **climate entity's temperature control**, you must properly configure your heater's physical thermostat in MyVoltalis.

  **Important:** The Voltalis device cannot generate a heating temperature higher than the one set on your heater. For temperature control to work correctly, make sure that your device's thermostat is set to a temperature higher than the one defined in the application.

  ### Configuration Steps

  1. Access your heater's physical thermostat (on the radiator itself)
  2. Set it to the maximum temperature you want to allow (e.g., 25°C or 30°C)
  3. Then use the Voltalis integration or MyVoltalis app to control the target temperature within this range

  ### Visual Guide

  Watch this video guide from MyVoltalis for proper configuration:

  <video controls src="https://myvoltalis.com/assets/A5-CAQOXgYD.mp4" title="guide"></video>

  *Video source: [MyVoltalis](https://myvoltalis.com/assets/A5-CAQOXgYD.mp4)*

  ### What Happens If Not Configured

  If your heater's physical thermostat is set lower than your desired temperature in Home Assistant:
  - The temperature control will not work as expected
  - Your heater will cap at its physical thermostat setting
  - You won't achieve the target temperature set in the app

</details>


## Entities

The integration creates different entities depending on the device type and capabilities:

### Climate Entity

<details>
  <summary>Climate Entity (Heating Devices Only)</summary>

  - **Entity ID**: `climate.<device_name>_climate`
  - **Type**: Climate (Thermostat)
  - **HVAC Modes**:
    - `Off`: Turn off the device
    - `Heat`: Manual heating mode
    - `Auto`: Automatic programming mode (follows user or default schedule)
  - **Preset Modes**: Comfort, Eco, Frost Protection, Temperature (depending on device capabilities)
  - **Temperature Control**: Set target temperature (7-30°C, 0.5°C steps)
    - ⚠️ **Important**: Before using temperature control, ensure your heater's physical thermostat is set higher than your desired target temperature. See the [Temperature Control Configuration](#important-temperature-control-configuration) section above.
  - **Features**:
    - Turn on/off
    - Change HVAC mode
    - Set preset mode
    - Adjust target temperature (if supported)
  - **Update Frequency**: Every 1 minute
</details>

### Water Heater Entity

<details>
  <summary>Water Heater Entity (Water Heating Devices Only)</summary>

  - **Entity ID**: `water_heater.<device_name>_water_heater`
  - **Type**: Water Heater
  - **Operation Modes**:
    - `Off`: The water heater is turned off (no heating allowed)
    - `On`: The water heater is allowed to operate (not a forced heating mode). If the device is behind a peak/off-peak (HP/HC) relay, it will only heat when the relay allows it. This mode does not override the relay or force heating.
    - `Auto`: Voltalis manages the water heater's on/off state according to its own schedule. However, if the device is behind a HP/HC relay, the relay always has priority: Voltalis can only allow or prevent heating when the relay is closed (off-peak). Voltalis cannot force the water heater to heat during peak hours if the relay is open.
    - `Away`: The water heater is in away mode (reduced or no heating, for periods of absence).
  - **Features**:
    - Turn on/off
    - Change operation mode (including away)
  - **Update Frequency**: Every 1 minute
</details>


### Sensors

<details>
  <summary>Energy Consumption Sensor</summary>

  - **Entity ID**: `sensor.<device_name>_device_consumption`
  - **Type**: Energy sensor
  - **Unit**: Wh (Watt-hours)
  - **Device Class**: Energy
  - **State Class**: Total Increasing
  - **Description**: Shows the cumulative energy consumption of the device
  - **Update Frequency**: Every 1 hour
</details>

<details>
  <summary>Connection Status Sensor</summary>Sensor</summary>

  - **Entity ID**: `sensor.<device_name>_device_connected`
  - **Type**: Enum sensor
  - **Device Class**: Enum
  - **States**: `Connected`, `Disconnected`, `Test in progress`
  - **Description**: Indicates the connection status of the device
  - **Update Frequency**: Every 1 minute
</details>

<details>
  <summary>Current Mode Sensor</summary>Sensor</summary>

  - **Entity ID**: `sensor.<device_name>_device_current_mode`
  - **Type**: Enum sensor
  - **Device Class**: Enum
  - **States**: `Comfort`, `Eco`, `Frost Protection`, `Temperature`, `On`, `Off`
  - **Description**: Shows the current operating mode of the device
  - **Icon**: Changes dynamically based on the current mode
  - **Update Frequency**: Every 1 minute
</details>

<details>
  <summary>Programming Sensor (Disabled by Default)</summary>fault)</summary>

  - **Entity ID**: `sensor.<device_name>_device_programming`
  - **Type**: Enum sensor
  - **Device Class**: Enum
  - **States**: `Manual`, `Default`, `User`, `Quick`
  - **Description**: Indicates which type of programming is currently active
  - **Icon**: Changes dynamically based on the programming type
  - **Update Frequency**: Every 1 minute
  - **Note**: This sensor is disabled by default. Enable it in the entity settings if needed.
</details>

### Energy Contract Sensors

The integration also provides sensors related to your energy contract:

<details>
  <summary>Subscribed Power Sensor</summary>

  - **Entity ID**: `sensor.voltalis_energy_contract_subscribed_power`
  - **Type**: Sensor
  - **Unit**: kVA (Kilovolt-ampere)
  - **Device Class**: Apparent Power
  - **Description**: Shows your subscribed power level from your energy contract
  - **Icon**: `mdi:meter-electric`
  - **Update Frequency**: Updates when contract data changes
</details>

<details>
  <summary>Energy Contract Current Mode Sensor</summary>

  - **Entity ID**: `sensor.voltalis_energy_contract_current_mode`
  - **Type**: Sensor
  - **States**: `Base`, `Peak`, `Off-Peak`
  - **Description**: Indicates the current pricing period of your energy contract
  - **Icon**: Changes dynamically based on the current mode
    - Base: `mdi:sort-calendar-today`
    - Peak: `mdi:sort-calendar-descending`
    - Off-Peak: `mdi:sort-calendar-ascending`
  - **Update Frequency**: Every 1 minute (automatically switches based on your contract's peak/off-peak hours)
</details>

<details>
  <summary>kWh Current Cost Sensor</summary>

  - **Entity ID**: `sensor.voltalis_energy_contract_kwh_current_cost`
  - **Type**: Monetary sensor
  - **Unit**: € (Euro)
  - **Device Class**: Monetary
  - **Description**: Shows the current cost per kWh based on whether you're in peak or off-peak hours (or base rate)
  - **Icon**: Changes dynamically based on the current pricing mode
    - Base: `mdi:gauge`
    - Peak: `mdi:gauge-full`
    - Off-Peak: `mdi:gauge-low`
  - **Update Frequency**: Every 1 minute (updates automatically when switching between peak/off-peak)
</details>

<details>
  <summary>kWh Peak Cost Sensor</summary>

  - **Entity ID**: `sensor.voltalis_energy_contract_kwh_peak_cost`
  - **Type**: Monetary sensor
  - **Unit**: € (Euro)
  - **Device Class**: Monetary
  - **Description**: Shows the cost per kWh during peak hours
  - **Icon**: `mdi:currency-eur`
  - **Update Frequency**: Updates when contract data changes
  - **Note**: Only available for peak/off-peak contracts
</details>

<details>
  <summary>kWh Off-Peak Cost Sensor</summary>

  - **Entity ID**: `sensor.voltalis_energy_contract_kwh_off_peak_cost`
  - **Type**: Monetary sensor
  - **Unit**: € (Euro)
  - **Device Class**: Monetary
  - **Description**: Shows the cost per kWh during off-peak hours
  - **Icon**: `mdi:currency-eur`
  - **Update Frequency**: Updates when contract data changes
  - **Note**: Only available for peak/off-peak contracts
</details>

### Select Entity

<details>
  <summary>Preset Selector</summary>lector</summary>

  - **Entity ID**: `select.<device_name>_device_preset`
  - **Type**: Select
  - **Options**: Auto, On (if available), Comfort, Eco, Frost Protection, Temperature, Off
  - **Description**: Allows quick switching between different operating modes
  - **Icon**: Changes dynamically based on the selected preset
  - **Features**:
    - **Auto**: Returns device to automatic programming (managed by Voltalis)
    - **On**: Turns device on in normal mode (if supported)
    - **Comfort/Eco/Frost Protection**: Activates the selected preset mode indefinitely
    - **Temperature**: Uses the current target temperature setting
      - ⚠️ **Important**: Before using this preset, ensure your heater's physical thermostat is properly configured. See the [Temperature Control Configuration](#important-temperature-control-configuration) section above.
    - **Off**: Turns the device off
  - **Update Frequency**: Every 1 minute
</details>

## Troubleshooting

### Authentication Errors

If you encounter authentication errors:

1. Verify your credentials are correct by logging into the [Voltalis website](https://www.voltalis.com)
2. Try reconfiguring the integration with updated credentials
3. If the problem persists, remove the integration and add it again

### Devices Not Showing Up

If your devices are not appearing:

1. Make sure your devices are properly configured in the Voltalis mobile app
2. Check that your devices are online and connected in the Voltalis app
3. Try restarting Home Assistant
4. If issues persist, check the Home Assistant logs for error messages

### Connection Issues

If you experience connection problems:

1. Check your internet connection
2. Verify that Home Assistant can access external services
3. Check the Home Assistant logs for specific error messages related to Voltalis

### Viewing Logs

To view detailed logs for troubleshooting:

1. Go to **Settings** > **System** > **Logs**
2. Search for "voltalis" to filter relevant log entries
3. You can also enable debug logging by adding this to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.voltalis: debug
```

## Removal

To remove the Voltalis integration:

1. Go to **Settings** > **Devices & Services**
2. Find the Voltalis integration
3. Click on the **⋮** menu and select **Delete**
4. Confirm the deletion

All entities and devices associated with the integration will be removed from Home Assistant.

If you also want to remove the integration files:

1. Navigate to your Home Assistant `custom_components` directory
2. Delete the `voltalis` folder
3. Restart Home Assistant

## Data Privacy

This integration communicates directly with the Voltalis API using your credentials. Your credentials are stored securely in Home Assistant's encrypted storage. No data is sent to any third party other than Voltalis's official servers.

## Supported Devices

This integration supports all devices that are compatible with the Voltalis ecosystem, including:

- **Voltalis Modulator (Wire)**: Connected heating modulators for wire-controlled heaters
  - Provides: Climate entity, all sensors, preset selector
- **Voltalis Modulator (Relay)**: Connected heating modulators for relay-controlled heaters
  - Provides: Climate entity, all sensors, preset selector
- **Water Heaters**: Water heating devices with Voltalis modulators
  - Provides: Consumption sensor, connection status sensor, preset selector

All devices provide energy consumption and connection status monitoring. Heating devices additionally provide full climate control with thermostat functionality.

## Service Actions

The integration provides advanced service actions for climate entities to enable sophisticated automations:

### Set Manual Mode

Service: `voltalis.set_manual_mode`

Set the device to manual mode with a specific preset or temperature for a defined duration or indefinitely.

**Parameters:**
- `preset_mode` (optional): The preset mode to apply (comfort, eco, frost_protection, none)
- `temperature` (optional): Target temperature in Celsius. If set, the device will use temperature mode
- `duration_hours` (optional): How long to stay in manual mode (in hours). If not specified, stays in manual mode until further notice

**Examples:**

```yaml
# Set to Comfort mode for 3 hours
service: voltalis.set_manual_mode
target:
  entity_id: climate.living_room_heater
data:
  preset_mode: comfort
  duration_hours: 3

# Set to 21°C indefinitely
service: voltalis.set_manual_mode
target:
  entity_id: climate.bedroom_heater
data:
  temperature: 21

# Set to Eco mode with custom temperature for 5 hours
service: voltalis.set_manual_mode
target:
  entity_id: climate.kitchen_heater
data:
  preset_mode: eco
  temperature: 19.5
  duration_hours: 5
```

### Disable Manual Mode

Service: `voltalis.disable_manual_mode`

Return the device to automatic planning mode (user or default schedule).

**Example:**

```yaml
service: voltalis.disable_manual_mode
target:
  entity_id: climate.living_room_heater
```

### Set Quick Boost

Service: `voltalis.set_quick_boost`

Quickly boost heating for a short period. Useful for rapid heating before arriving home.

**Parameters:**
- `temperature` (optional): Target temperature for boost mode. If not specified, uses comfort mode with increased temperature
- `duration_hours` (optional): How long to boost heating (in hours). Default is 2 hours

**Examples:**

```yaml
# Quick 2-hour boost at comfort temperature
service: voltalis.set_quick_boost
target:
  entity_id: climate.living_room_heater

# Boost to 23°C for 1 hour
service: voltalis.set_quick_boost
target:
  entity_id: climate.bathroom_heater
data:
  temperature: 23
  duration_hours: 1
```

### Usage in Automations

These service actions are particularly useful for creating automations:

```yaml
# Boost heating when arriving home
automation:
  - alias: "Boost heating on arrival"
    trigger:
      - platform: zone
        entity_id: person.john
        zone: zone.home
        event: enter
    action:
      - service: voltalis.set_quick_boost
        target:
          entity_id: climate.living_room_heater
        data:
          duration_hours: 2

# Set eco mode at night
automation:
  - alias: "Night eco mode"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: voltalis.set_manual_mode
        target:
          entity_id: climate.bedroom_heater
        data:
          preset_mode: eco
          duration_hours: 8

# Return to auto mode in the morning
automation:
  - alias: "Morning auto mode"
    trigger:
      - platform: time
        at: "06:00:00"
    action:
      - service: voltalis.disable_manual_mode
        target:
          entity_id: climate.bedroom_heater
```

## Inspirations

This project was inspired by and built upon the work of:

- [ha-voltalis from jdelahayes](https://github.com/jdelahayes/ha-voltalis)
- [ha-addons from zaosoula](https://github.com/zaosoula/ha-addons)
- [flashbird-homeassistant from gorfo66](https://github.com/gorfo66/flashbird-homeassistant)

## Contributing

Contributions are welcome! Please make sure to follow the [Contribution guidelines](CONTRIBUTING.md) to open an issue or submit a pull request. Issues not conforming to the guidelines may be closed immediately.

## License

This project is [MIT licensed](LICENSE).
