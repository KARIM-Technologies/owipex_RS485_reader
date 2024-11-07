# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: PH Sensor ID Configuration V0.2
# Description: Interactive script to set the PH Sensor device ID
# -----------------------------------------------------------------------------

import serial
import struct
import crcmod.predefined
import logging
import time

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def test_communication(ser, device_id):
    """Test communication with the sensor"""
    function_code = 0x03
    register_address = 0x0001  # PH value register
    register_count = 0x0002    # Read 2 registers for float value
    
    message = struct.pack('>BBHH', device_id, function_code, register_address, register_count)
    crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')(message)
    message += struct.pack('<H', crc16)
    
    ser.write(message)
    response = ser.read(9)  # Device ID + Function Code + Byte Count + 4 Data Bytes + 2 CRC Bytes
    
    if len(response) == 9:
        logging.info(f"Kommunikation mit Gerät {device_id} erfolgreich")
        return True
    else:
        logging.error(f"Keine Antwort von Gerät {device_id}")
        return False

def write_device_id(old_device_id, new_device_id, port='/dev/ttyS0'):
    """Change the device ID of the PH sensor"""
    ser = serial.Serial(
        port=port,
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=1,
        bytesize=8,
        timeout=1
    )

    try:
        # Test communication first
        logging.info(f"Teste Kommunikation mit aktueller Adresse {old_device_id}...")
        if not test_communication(ser, old_device_id):
            raise Exception("Kommunikationstest fehlgeschlagen")

        # Write new address
        function_code = 0x06  # Write Single Register
        register_address = 0x0019  # Device ID register for PH sensor
        
        message = struct.pack('>BBHH', old_device_id, function_code, register_address, new_device_id)
        crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')(message)
        message += struct.pack('<H', crc16)

        logging.info(f"Ändere Geräteadresse zu {new_device_id}...")
        ser.write(message)
        response = ser.read(8)  # Response for Write Single Register

        if len(response) != 8:
            raise Exception("Keine gültige Antwort bei Adressänderung")

        # Wait for device to apply new address
        logging.info("Warte 5 Sekunden auf Geräte-Reset...")
        time.sleep(5)

        # Verify new address
        logging.info("Verifiziere neue Adresse...")
        if test_communication(ser, new_device_id):
            logging.info("Neue Adresse erfolgreich verifiziert")
            return True
        else:
            raise Exception("Konnte neue Adresse nicht verifizieren")

    finally:
        ser.close()

def main():
    setup_logging()
    
    print("\n=== PH-Sensor Adresskonfiguration ===\n")
    
    # Get current address
    while True:
        try:
            current_address = int(input("Bitte geben Sie die aktuelle Geräteadresse ein (1-247): "))
            if 1 <= current_address <= 247:
                break
            print("Ungültige Eingabe: Adresse muss zwischen 1 und 247 liegen")
        except ValueError:
            print("Ungültige Eingabe: Bitte geben Sie eine Zahl ein")

    # Get new address
    while True:
        try:
            new_address = int(input("Bitte geben Sie die neue Geräteadresse ein (1-247): "))
            if 1 <= new_address <= 247:
                break
            print("Ungültige Eingabe: Adresse muss zwischen 1 und 247 liegen")
        except ValueError:
            print("Ungültige Eingabe: Bitte geben Sie eine Zahl ein")

    # Get port (optional)
    port = input("Bitte geben Sie den seriellen Port ein (Enter für /dev/ttyS0): ").strip()
    if not port:
        port = '/dev/ttyS0'

    # Confirmation
    confirm = input(f"\nWARNUNG: Möchten Sie die Geräteadresse wirklich von {current_address} "
                   f"zu {new_address} ändern? (j/N): ")
    
    if confirm.lower() != 'j':
        logging.info("Adressänderung abgebrochen.")
        return

    try:
        write_device_id(current_address, new_address, port)
        logging.info(f"Geräteadresse erfolgreich von {current_address} zu {new_address} geändert")
    except Exception as e:
        logging.error(f"Fehler beim Konfigurieren des PH-Sensors: {e}")

if __name__ == "__main__":
    main() 