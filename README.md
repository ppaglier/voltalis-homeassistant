# Voltalis Home Assistant Integration

[![Quality Scale](https://img.shields.io/badge/quality-silver-c0c0c0)](https://developers.home-assistant.io/docs/integration_quality_scale_index/) [![Install with HACS](https://my.home-assistant.io/badges/hacs.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ppaglier&repository=voltalis-homeassistant&category=integration) [![Add Integration](https://my.home-assistant.io/badges/config_flow.svg)](https://my.home-assistant.io/redirect/config_flow/?domain=voltalis)

## About Voltalis

Voltalis is a French company that provides smart energy management solutions to help households and businesses reduce electricity consumption and support grid stability. Their innovative technology helps optimize energy usage while maintaining comfort, allowing users to:

- Monitor real-time energy consumption of their heating and water heating devices
- Reduce electricity bills through smart energy management
- Contribute to grid stability and environmental sustainability
- Gain insights into their energy usage patterns

You can learn more about their solutions on their official website: [https://www.voltalis.com](https://www.voltalis.com).

This integration allows you to connect your Voltalis devices to Home Assistant, enabling you to monitor your energy consumption and device connectivity status directly from your Home Assistant dashboard.

## Features

This integration provides the following entities for each Voltalis device:

- **Energy Consumption Sensor**: Monitor the hourly energy consumption of your devices (in Wh)
- **Connectivity Binary Sensor**: Check if your devices are online and connected to the Voltalis network

## Installation

### Prerequisites

Before installing this integration, you need:

- A valid Voltalis account (the email and password you use to connect to the Voltalis mobile app or website)
- At least one Voltalis device installed and configured in your home
- Home Assistant 2024.1.0 or newer

### Installation via HACS (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed in your Home Assistant instance
2. In Home Assistant, go to **HACS** > **Integrations**
3. Click on the **⋮** menu in the top-right corner and select **Custom repositories**
4. Add this repository URL: `https://github.com/ppaglier/voltalis-homeassistant`
5. Set category to **Integration**
6. Click **Add**
7. Search for "Voltalis" in HACS and click **Download**
8. Restart Home Assistant

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/ppaglier/voltalis-homeassistant/releases)
2. Extract the `custom_components/voltalis` folder from the archive
3. Copy the `voltalis` folder to your Home Assistant `custom_components` directory:
   - If the `custom_components` directory doesn't exist, create it in your Home Assistant configuration directory (where `configuration.yaml` is located)
   - The final path should be: `<config_dir>/custom_components/voltalis/`
4. Restart Home Assistant

## Configuration

### Adding the Integration

1. In Home Assistant, go to **Settings** > **Devices & Services**
2. Click on the **+ Add Integration** button
3. Search for "Voltalis" and select it
4. Enter your Voltalis credentials:
   - **Email address**: The email address associated with your Voltalis account
   - **Password**: Your Voltalis account password
5. Click **Submit**

The integration will validate your credentials and automatically discover all your Voltalis devices.

### Reconfiguration

If you need to update your credentials:

1. Go to **Settings** > **Devices & Services**
2. Find the Voltalis integration
3. Click on the **⋮** menu and select **Reconfigure**
4. Enter your new credentials
5. Click **Submit**

## Entities

For each Voltalis device, the integration creates the following entities:

### Energy Sensor

- **Entity ID**: `sensor.<device_name>_consumption`
- **Type**: Energy sensor
- **Unit**: Wh (Watt-hours)
- **Device Class**: Energy
- **State Class**: Total Increasing
- **Description**: Shows the cumulative energy consumption of the device
- **Update Frequency**: Every 1 minutes

### Connectivity Binary Sensor

- **Entity ID**: `binary_sensor.<device_name>_connection_status`
- **Type**: Connectivity binary sensor
- **Device Class**: Connectivity
- **States**:
  - `on`: Device is connected and online
  - `off`: Device is disconnected or offline
- **Update Frequency**: Every 1 minutes

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
- **Voltalis Modulator (Relay)**: Connected heating modulators for relay-controlled heaters
- **Water Heaters**: Water heating devices with Voltalis modulators

## Service Actions

This integration does not currently provide any service actions. All functionality is exposed through sensors and binary sensors that can be used in automations and dashboards.

## Inspirations

This project was inspired by and built upon the work of:

- [ha-voltalis from jdelahayes](https://github.com/jdelahayes/ha-voltalis)
- [ha-addons from zaosoula](https://github.com/zaosoula/ha-addons)
- [flashbird-homeassistant from gorfo66](https://github.com/gorfo66/flashbird-homeassistant)

## Contributing

Contributions are welcome! Please make sure to follow the [Contribution guidelines](CONTRIBUTING.md) to open an issue or submit a pull request. Issues not conforming to the guidelines may be closed immediately.

## License

This project is [MIT licensed](LICENSE).
