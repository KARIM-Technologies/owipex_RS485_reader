# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: Flow Sensor ID Configuration V0.1
# Description: Script to set the Flow Sensor device ID to 0x04
# -----------------------------------------------------------------------------

import serial
import struct
import crcmod.predefined

def write_device_id(old_device_id, new_device_id, port='/dev/ttyS0'):
    function_code = 0x06  # Function code for Write Single Register
    register_address = 0x0019  # Address for the device id register
    crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')

    message = struct.pack('>B B H H', old_device_id, function_code, register_address, new_device_id)
    message += struct.pack('<H', crc16(message))

    ser = serial.Serial(port=port, baudrate=9600, parity=serial.PARITY_NONE, stopbits=1, bytesize=8, timeout=1)
    ser.write(message)

    response = ser.read(8)  # Response size for Write Single Register is always 8 bytes

    if len(response) < 8:
        raise Exception('Invalid response: less than 8 bytes')

    received_device_id, received_function_code, received_register_address, received_value, received_crc = struct.unpack('>B B H H H', response)

    print(f'Response from device:')
    print(f'Device ID: {received_device_id} (0x{received_device_id:02x} in hexadecimal)')
    print(f'Function code: {received_function_code} (0x{received_function_code:02x} in hexadecimal)')
    print(f'Register address: {received_register_address} (0x{received_register_address:04x} in hexadecimal)')
    print(f'Written value (new device id): {received_value} (0x{received_value:04x} in hexadecimal)')
    print(f'CRC: 0x{received_crc:04x}')

if __name__ == "__main__":
    print("Configuring Flow Sensor ID...")
    try:
        # Change device ID to 0x04
        write_device_id(0x01, 0x04)  # Assuming current ID is 0x01
        print("Successfully configured Flow Sensor ID to 0x04")
    except Exception as e:
        print(f"Error configuring Flow Sensor: {e}")