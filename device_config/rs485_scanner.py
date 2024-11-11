# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: RS485 Scanner V0.1
# Description: Tool to scan for RS485 devices and identify their type
# -----------------------------------------------------------------------------

import serial
import struct
import crcmod.predefined
import logging
import time
from typing import Dict, Optional

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

class RS485Scanner:
    def __init__(self, port='/dev/ttyS0'):
        self.port = port
        self.ser = serial.Serial(
            port=port,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=1,
            bytesize=8,
            timeout=0.3  # Kurzes Timeout für schnelleres Scannen
        )
        self.crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')

    def test_radar_sensor(self, address: int) -> bool:
        """Test ob ein Radar-Sensor unter dieser Adresse antwortet"""
        message = struct.pack('>BBHH', address, 0x03, 0x0000, 0x0001)
        message += struct.pack('<H', self.crc16(message))
        
        self.ser.write(message)
        response = self.ser.read(7)
        
        if len(response) == 7:
            value = struct.unpack('>H', response[3:5])[0]
            return True
        return False

    def test_ph_sensor(self, address: int) -> bool:
        """Test ob ein PH-Sensor unter dieser Adresse antwortet"""
        message = struct.pack('>BBHH', address, 0x03, 0x0001, 0x0002)
        message += struct.pack('<H', self.crc16(message))
        
        self.ser.write(message)
        response = self.ser.read(9)
        
        return len(response) == 9

    def test_turbidity_sensor(self, address: int) -> bool:
        """Test ob ein Trübungssensor unter dieser Adresse antwortet"""
        message = struct.pack('>BBHH', address, 0x03, 0x0001, 0x0002)
        message += struct.pack('<H', self.crc16(message))
        
        self.ser.write(message)
        response = self.ser.read(9)
        
        return len(response) == 9

    def test_flow_sensor(self, address: int) -> bool:
        """Test ob ein Durchflusssensor unter dieser Adresse antwortet"""
        message = struct.pack('>BBHH', address, 0x03, 0x0009, 0x0002)
        message += struct.pack('<H', self.crc16(message))
        
        self.ser.write(message)
        response = self.ser.read(9)
        
        return len(response) == 9

    def identify_device(self, address: int) -> Optional[str]:
        """Identifiziert den Gerätetyp unter der gegebenen Adresse"""
        if self.test_radar_sensor(address):
            return "Radar-Sensor"
        elif self.test_ph_sensor(address):
            return "PH-Sensor"
        elif self.test_turbidity_sensor(address):
            return "Trübungssensor"
        elif self.test_flow_sensor(address):
            return "Durchflusssensor"
        return None

    def scan_range(self, start_addr: int = 1, end_addr: int = 247) -> Dict[int, str]:
        """Scannt einen Adressbereich nach Geräten"""
        found_devices = {}
        
        print("\nScanne RS485-Bus nach Geräten...\n")
        print("Adresse | Gerätetyp")
        print("-" * 30)
        
        for addr in range(start_addr, end_addr + 1):
            device_type = self.identify_device(addr)
            if device_type:
                found_devices[addr] = device_type
                print(f"{addr:7} | {device_type}")
                
        return found_devices

    def close(self):
        """Schließt die serielle Verbindung"""
        self.ser.close()

def main():
    setup_logging()
    
    print("\n=== RS485 Geräte-Scanner ===\n")
    
    # Get port (optional)
    port = input("Bitte geben Sie den seriellen Port ein (Enter für /dev/ttyS0): ").strip()
    if not port:
        port = '/dev/ttyS0'

    # Get address range (optional)
    try:
        start_addr = input("Startadresse für Scan (Enter für 1): ").strip()
        start_addr = int(start_addr) if start_addr else 1

        end_addr = input("Endadresse für Scan (Enter für 247): ").strip()
        end_addr = int(end_addr) if end_addr else 247

        if not (1 <= start_addr <= 247 and 1 <= end_addr <= 247 and start_addr <= end_addr):
            raise ValueError("Ungültiger Adressbereich")
    except ValueError as e:
        logging.error(f"Fehler bei der Adresseingabe: {e}")
        return

    scanner = None
    try:
        scanner = RS485Scanner(port)
        found_devices = scanner.scan_range(start_addr, end_addr)
        
        if not found_devices:
            print("\nKeine Geräte gefunden!")
        else:
            print(f"\nGefundene Geräte: {len(found_devices)}")
            
    except Exception as e:
        logging.error(f"Fehler beim Scannen: {e}")
    finally:
        if scanner:
            scanner.close()

if __name__ == "__main__":
    main() 