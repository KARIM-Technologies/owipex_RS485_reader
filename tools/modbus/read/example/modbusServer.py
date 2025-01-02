# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: Modbus Sensor Server V0.1
# Description: Modbus Sensor Server
# -----------------------------------------------------------------------------

# This script tests the functions of the Modbus Sensor Server by KARIM Technologies.


import subprocess
import time
from libs.modbus_lib import DeviceManager

def publish_mqtt(topic, message, device_token):
    command = f"mosquitto_pub -d -q 1 -h 192.168.178.47 -p 1883 -t {topic} -u \"{device_token}\" -m '{message}'"
    subprocess.run(command, shell=True)
    print(f"Executing: {command}")

# DeviceManager-Erstellung und Konfiguration
dev_manager = DeviceManager(port='/dev/ttyS0', baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=1)
dev_manager.add_device(device_id=0x01)
dev_manager.add_device(device_id=0x02)
dev_manager.add_device(device_id=0x03)


count = 2
interval = 10  # Zeitintervall in Sekunden
device_token = "xyinFxry150wocL6LY7f"

while True:
    # Radar-Sensor Daten lesen und Mittelwert berechnen
    radar_read_values = [dev_manager.get_device(0x01).read_radar_sensor(register_address=0x0000)]
    radar_avg_value = sum(filter(None, radar_read_values)) / len(radar_read_values) if radar_read_values else 'null'
    radar_message = f'{{"Radar_Height":{radar_avg_value}}}'
    publish_mqtt(f"v1/devices/me/telemetry", radar_message, device_token)

    # Trübungssensor Daten lesen und Mittelwert berechnen
    trub_read_values = [dev_manager.get_device(0x03).read_register(0x0001, 2, '>f') for _ in range(count)]  # Angepasste Startadresse und Registeranzahl für Trübungssensor
    trub_avg_value = sum(filter(None, trub_read_values)) / len(trub_read_values) if trub_read_values else 'null'
    trub_message = f'{{"Turb_Value":{trub_avg_value}}}'
    publish_mqtt(f"v1/devices/me/telemetry", trub_message, device_token)

    # PH-Sensor Daten lesen und Mittelwert berechnen
    ph_read_values = [dev_manager.get_device(0x03).read_register(0x0001, 2, '>f') for _ in range(count)]  # Angepasste Startadresse und Registeranzahl für PH-Sensor
    ph_avg_value = sum(filter(None, ph_read_values)) / len(ph_read_values) if ph_read_values else 'null'
    ph_message = f'{{"PH_Value":{ph_avg_value}}}'
    publish_mqtt(f"v1/devices/me/telemetry", ph_message, device_token)

    # PH-Sensor Daten lesen und Mittelwert berechnen
    ph_read_values = [dev_manager.get_device(0x03).read_register(0x0003, 2, '>f') for _ in range(count)]  # Angepasste Startadresse und Registeranzahl für PH-Sensor
    ph_avg_value = sum(filter(None, ph_read_values)) / len(ph_read_values) if ph_read_values else 'null'
    ph_message = f'{{"PH_Temp":{ph_avg_value}}}'
    publish_mqtt(f"v1/devices/me/telemetry", ph_message, device_token)
    
    time.sleep(interval)