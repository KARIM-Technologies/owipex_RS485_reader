# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: Modbus Lib V0.6
# Description: Modbus Communication Test Script
# -----------------------------------------------------------------------------

# This script tests the functions of the Modbus library by KARIM Technologies.
# Two sensors are connected to the same port, and their temperature values, as well as another value, are read.

from libs.modbus_lib import DeviceManager

# Create DeviceManager
dev_manager = DeviceManager(port='/dev/ttyS0', baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=1)

# Add devices
dev_manager.add_device(device_id=0x01)
dev_manager.add_device(device_id=0x02)
dev_manager.add_device(device_id=0x03)

# Get devices and read their registers
Radar_Sensor = dev_manager.get_device(device_id=0x01)
Trub_Sensor = dev_manager.get_device(device_id=0x02)
PH_Sensor = dev_manager.get_device(device_id=0x03)

# Read radar sensor values
air_height = Radar_Sensor.read_radar_sensor(register_address=0x0000)
liquid_level = Radar_Sensor.read_radar_sensor(register_address=0x0002)
print(f'Air Height: {air_height} mm')

# Read temperatures
tempPHSens = PH_Sensor.read_register(start_address=0x0003, register_count=2)
tempTruebSens = Trub_Sensor.read_register(start_address=0x0003, register_count=2)
print(f'tempPHSens: {tempPHSens}, tempTruebSens: {tempTruebSens}')

# Read other values
PHValue = PH_Sensor.read_register(start_address=0x0001, register_count=2)
TruebValue = Trub_Sensor.read_register(start_address=0x0001, register_count=2)
print(f'PH Wert: {PHValue}, Truebung: {TruebValue}')

# To stop auto read
# dev_manager.auto_read = False