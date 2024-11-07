# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: Radar Sensor ID Configuration V0.1
# Description: Script to set the Radar Sensor device ID
# -----------------------------------------------------------------------------

import serial
import struct
import crcmod.predefined
import logging
import time
import argparse

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def write_device_id(old_device_id, new_device_id, port='/dev/ttyS0'):
    """
    Ändert die Geräte-ID des Radarsensors
    
    Args:
        old_device_id: Aktuelle Geräteadresse
        new_device_id: Neue gewünschte Geräteadresse
        port: Serieller Port (Standard: /dev/ttyS0)
    """
    function_code = 0x06  # Function code for Write Single Register
    register_address = 0x2000  # Address for the device id register
    crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')

    # Test communication first
    test_message = struct.pack('>B B H H', old_device_id, 0x03, 0x0001, 1)
    test_message += struct.pack('<H', crc16(test_message))

    ser = serial.Serial(
        port=port,
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=1,
        bytesize=8,
        timeout=1
    )

    # Test reading
    ser.write(test_message)
    test_response = ser.read(7)
    if len(test_response) != 7:
        raise Exception('Keine Antwort vom Gerät bei Kommunikationstest')

    # Write new address
    message = struct.pack('>B B H H', old_device_id, function_code, register_address, new_device_id)
    message += struct.pack('<H', crc16(message))

    ser.write(message)
    response = ser.read(8)  # Response size for Write Single Register is always 8 bytes

    if len(response) < 8:
        raise Exception('Ungültige Antwort: weniger als 8 Bytes')

    received_device_id, received_function_code, received_register_address, received_value, received_crc = struct.unpack('>B B H H H', response)

    print(f'Antwort vom Gerät:')
    print(f'Geräte ID: {received_device_id} (0x{received_device_id:02x} hex)')
    print(f'Funktionscode: {received_function_code} (0x{received_function_code:02x} hex)')
    print(f'Register-Adresse: {received_register_address} (0x{received_register_address:04x} hex)')
    print(f'Geschriebener Wert (neue ID): {received_value} (0x{received_value:04x} hex)')
    print(f'CRC: 0x{received_crc:04x}')

    # Wait and verify
    time.sleep(2)
    
    # Test new address
    test_message = struct.pack('>B B H H', new_device_id, 0x03, 0x0001, 1)
    test_message += struct.pack('<H', crc16(test_message))
    
    ser.write(test_message)
    verify_response = ser.read(7)
    
    if len(verify_response) != 7:
        raise Exception('Konnte neue Adresse nicht verifizieren')

    ser.close()

if __name__ == "__main__":
    setup_logging()
    parser = argparse.ArgumentParser(description='Radar Sensor Address Configuration')
    parser.add_argument('--port', type=str, default='/dev/ttyS0',
                      help='Serieller Port (Standard: /dev/ttyS0)')
    parser.add_argument('--current-address', type=int, default=1,
                      help='Aktuelle Geräteadresse (Standard: 1)')
    parser.add_argument('--new-address', type=int, required=True,
                      help='Neue Geräteadresse (1-247)')

    args = parser.parse_args()

    if not 1 <= args.new_address <= 247:
        logging.error("Neue Adresse muss zwischen 1 und 247 liegen!")
        exit(1)

    confirm = input(f"WARNUNG: Möchten Sie die Geräteadresse wirklich von {args.current_address} "
                   f"zu {args.new_address} ändern? (j/N): ")
    
    if confirm.lower() != 'j':
        logging.info("Adressänderung abgebrochen.")
        exit(0)

    try:
        write_device_id(args.current_address, args.new_address, args.port)
        logging.info(f"Geräteadresse erfolgreich von {args.current_address} zu {args.new_address} geändert")
    except Exception as e:
        logging.error(f"Fehler beim Konfigurieren des Radarsensors: {e}")
        exit(1) 