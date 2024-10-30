# Device Configuration Scripts

These scripts are used to configure the Modbus device IDs for various sensors in the system.

## Device IDs

- Radar Sensor: 0x01 (default, unchanged)
- Turbidity Sensor: 0x02
- PH Sensor: 0x03
- Flow Sensor: 0x04

## Usage

To configure each sensor, run the appropriate script:

```bash
# Configure Flow Sensor
python3 flow_sensor_config.py

# Configure Turbidity Sensor
python3 turbidity_sensor_config.py

# Configure PH Sensor
python3 ph_sensor_config.py
```

**Important Notes:**
- Run these scripts only when setting up new sensors or reconfiguring existing ones
- Each script assumes the current device ID is 0x01 (factory default)
- Make sure only one sensor is connected when running each configuration script
- Run scripts with sudo if required for serial port access