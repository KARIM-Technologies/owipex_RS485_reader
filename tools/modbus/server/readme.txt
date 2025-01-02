# Modbus Sensor Server V0.1

## Overview
This script is designed to test the functions of the Modbus Sensor Server by KARIM Technologies. It continuously reads data from Modbus sensors connected to a serial port and publishes the readings to an MQTT server.

## Configuration
- **Port:** `/dev/ttyS0`
- **Baud Rate:** 9600
- **Parity:** None (N)
- **Stop Bits:** 1
- **Byte Size:** 8 bits
- **Timeout:** 1 second

## Devices
The script is configured to handle multiple devices:
- Device ID `0x01`: Radar Sensor
- Device ID `0x02`: (Not used in the current configuration)
- Device ID `0x03`: Turbidity and PH Sensor

## Operation
The script performs the following operations in a loop:
1. **Radar Sensor Reading**: Reads the radar height from device `0x01`.
2. **Turbidity Sensor Reading**: Calculates the average turbidity value from device `0x03` using multiple readings.
3. **PH Sensor Reading**: Calculates the average PH value and temperature from device `0x03` using multiple readings.

## MQTT Publishing
For each sensor reading, the script publishes a message to the MQTT topic `v1/devices/me/telemetry` using the `mosquitto_pub` command. Each sensor value is published as a separate MQTT message with its corresponding device token.

### Example MQTT Command
```shell
mosquitto_pub -d -q 1 -h 192.168.178.47 -p 1883 -t v1/devices/me/telemetry -u "device_token" -m '{"Sensor_Name":value}'
