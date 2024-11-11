# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: Radar Sensor ID Configuration V0.2
# Description: Interactive script to set the Radar Sensor device ID
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
    register_address = 0x0000  # Air height register
    register_count = 0x0001    # Read 1 register
    
    message = struct.pack('>BBHH', device_id, function_code, register_address, register_count)
    crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')(message)
    message += struct.pack('<H', crc16)
    
    ser.write(message)
    response = ser.read(7)  # Device ID + Function Code + Byte Count + 2 Data Bytes + 2 CRC Bytes
    
    if len(response) == 7:
        value = struct.unpack('>H', response[3:5])[0]
        logging.info(f"Kommunikation mit Gerät {device_id} erfolgreich (Messwert: {value}mm)")
        return True
    else:
        logging.error(f"Keine Antwort von Gerät {device_id}")
        return False

def write_device_id(old_device_id, new_device_id, port='/dev/ttyS0'):
    """Change the device ID of the Radar sensor"""
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

        # Write new address using function code 0x10
        function_code = 0x10
        register_address = 0x2006  # Offset 6 for bus address
        register_count = 0x0001
        byte_count = 0x02
        
        # Validate new address range (1-32 according to documentation)
        if not 1 <= new_device_id <= 90:
            raise ValueError("Neue Adresse muss zwischen 1 und 32 liegen")
        
        # Prepare the value to write (U16 format)
        value_to_write = new_device_id & 0xFFFF  # Ensure 16-bit unsigned integer
        
        message = struct.pack('>BBHHBH', 
            old_device_id,      # Device address (1 byte)
            function_code,      # Function code 0x10 (1 byte)
            register_address,   # Register address 0x2006 (2 bytes)
            register_count,     # Number of registers (2 bytes)
            byte_count,        # Byte count (1 byte)
            value_to_write     # Value to write (2 bytes)
        )
        
        crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')(message)
        message += struct.pack('<H', crc16)

        logging.info(f"Sende Adressänderungsbefehl: {message.hex()}")
        ser.write(message)
        
        # Read response
        response = ser.read(8)  # Device ID + Function Code + Register Address + Register Count + CRC
        if len(response) != 8:
            raise Exception("Keine gültige Antwort bei Adressänderung")

        logging.info(f"Empfangene Antwort: {response.hex()}")
        
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
    
    print("\n=== Radar-Sensor Adresskonfiguration ===\n")
    
    # Get current address
    while True:
        try:
            current_address = int(input("Bitte geben Sie die aktuelle Geräteadresse ein (1-32): "))
            if 1 <= current_address <= 80:
                break
            print("Ungültige Eingabe: Adresse muss zwischen 1 und 32 liegen")
        except ValueError:
            print("Ungültige Eingabe: Bitte geben Sie eine Zahl ein")

    # Get new address
    while True:
        try:
            new_address = int(input("Bitte geben Sie die neue Geräteadresse ein (1-32): "))
            if 1 <= new_address <= 80:
                break
            print("Ungültige Eingabe: Adresse muss zwischen 1 und 32 liegen")
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
        logging.error(f"Fehler beim Konfigurieren des Radar-Sensors: {e}")

if __name__ == "__main__":
    main()