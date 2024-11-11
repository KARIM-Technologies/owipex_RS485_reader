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
    ser = serial.Serial(
        port=port,
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=1,
        bytesize=8,
        timeout=1
    )

    try:
        # Test communication first using function code 0x03 to read air height
        function_code_read = 0x03
        test_message = struct.pack('>BBHH', old_device_id, function_code_read, 0x0000, 0x0001)
        crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')(test_message)
        test_message += struct.pack('<H', crc16)

        logging.info("Teste Kommunikation...")
        ser.write(test_message)
        test_response = ser.read(7)  # Device ID + Function Code + Length + 2 Data Bytes + 2 CRC Bytes
        
        if len(test_response) != 7:
            raise Exception('Keine Antwort vom Gerät bei Kommunikationstest')
        
        logging.info("Kommunikationstest erfolgreich")

        # Write new address using function code 0x10
        function_code_write = 0x10
        register_address = 0x2006  # Starting address for device settings
        register_count = 0x0001    # Number of registers to write
        byte_count = 0x02         # Number of bytes to write (2 bytes per register)
        
        # Build message: ID + FN + ADDR + COUNT + BYTES + VALUE + CRC
        message = struct.pack('>BBHHBB', old_device_id, function_code_write, 
                            register_address, register_count, byte_count, new_device_id)
        crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')(message)
        message += struct.pack('<H', crc16)

        logging.info(f"Sende Adressänderungsbefehl: {message.hex()}")
        ser.write(message)
        
        # Read response
        response = ser.read(8)  # Device ID + Function Code + Register Address + Register Count + CRC
        if len(response) != 8:
            raise Exception('Ungültige Antwort bei Adressänderung')

        logging.info(f"Empfangene Antwort: {response.hex()}")
        
        # Wait for device to apply new address
        logging.info("Warte 5 Sekunden auf Geräte-Reset...")
        time.sleep(5)
        
        # Verify new address by reading air height
        verify_message = struct.pack('>BBHH', new_device_id, function_code_read, 0x0000, 0x0001)
        crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')(verify_message)
        verify_message += struct.pack('<H', crc16)
        
        logging.info("Verifiziere neue Adresse...")
        ser.write(verify_message)
        verify_response = ser.read(7)
        
        if len(verify_response) != 7:
            raise Exception('Konnte neue Adresse nicht verifizieren')
        
        logging.info(f"Neue Adresse {new_device_id} erfolgreich verifiziert")
        return True

    except Exception as e:
        logging.error(f"Fehler: {str(e)}")
        return False
    finally:
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
        if write_device_id(args.current_address, args.new_address, args.port):
            logging.info(f"Geräteadresse erfolgreich von {args.current_address} zu {args.new_address} geändert")
        else:
            logging.error("Adressänderung fehlgeschlagen")
            exit(1)
    except Exception as e:
        logging.error(f"Fehler beim Konfigurieren des Radarsensors: {e}")
        exit(1) 