# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: RS485 Port Tester V0.2
# Description: Tool to test RS485 ports with different sensor types
# -----------------------------------------------------------------------------

import serial
import struct
import crcmod.predefined
import logging
import time
import sys
from typing import Optional, Dict, Any

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        stream=sys.stdout  # Explizit auf stdout setzen
    )

class RS485PortTester:
    def __init__(self, port: str = '/dev/ttyS0'):
        try:
            self.port = port
            self.ser = serial.Serial(
                port=port,
                baudrate=9600,
                parity=serial.PARITY_NONE,
                stopbits=1,
                bytesize=8,
                timeout=1
            )
            self.crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')
            print(f"Port {port} erfolgreich geöffnet")
        except Exception as e:
            print(f"Fehler beim Öffnen des Ports {port}: {e}")
            raise

    def test_radar_sensor(self, device_id: int) -> Optional[Dict[str, Any]]:
        """Test Radar-Sensor und lese Messwerte"""
        try:
            print(f"Sende Anfrage an Radar-Sensor (ID: {device_id})...")
            message = struct.pack('>BBHH', device_id, 0x03, 0x0000, 0x0001)
            message += struct.pack('<H', self.crc16(message))
            
            print(f"Gesendete Nachricht: {message.hex()}")
            self.ser.write(message)
            
            response = self.ser.read(7)
            print(f"Empfangene Antwort: {response.hex() if response else 'Keine Antwort'}")
            
            if len(response) == 7:
                value = struct.unpack('>H', response[3:5])[0]
                return {"air_height": value}
            return None
        except Exception as e:
            print(f"Fehler beim Lesen des Radar-Sensors: {e}")
            return None

    # ... (andere Sensor-Test-Methoden bleiben gleich, aber mit zusätzlichen Print-Statements)

    def run_continuous_test(self, device_type: str, device_id: int, interval: float = 1.0):
        """Führt kontinuierliche Tests mit dem gewählten Gerät durch"""
        test_functions = {
            'radar': self.test_radar_sensor,
            'ph': self.test_ph_sensor,
            'turbidity': self.test_turbidity_sensor,
            'flow': self.test_flow_sensor
        }
        
        test_func = test_functions.get(device_type.lower())
        if not test_func:
            print(f"Unbekannter Gerätetyp: {device_type}")
            return

        print(f"\nStarte kontinuierlichen Test für {device_type}-Sensor (ID: {device_id})")
        print(f"Port: {self.port}")
        print(f"Intervall: {interval} Sekunden")
        print("Drücken Sie Ctrl+C zum Beenden\n")
        
        try:
            test_count = 0
            while True:
                test_count += 1
                print(f"\nTest #{test_count}")
                print("-" * 30)
                
                result = test_func(device_id)
                if result:
                    print(f"Erfolgreich gelesen - Werte: {result}")
                else:
                    print("Keine Antwort vom Gerät erhalten!")
                
                sys.stdout.flush()  # Erzwinge Ausgabe
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nTest durch Benutzer beendet.")
        except Exception as e:
            print(f"\nFehler während des Tests: {e}")

    def close(self):
        """Schließt die serielle Verbindung"""
        try:
            self.ser.close()
            print(f"Port {self.port} geschlossen")
        except Exception as e:
            print(f"Fehler beim Schließen des Ports: {e}")

def main():
    setup_logging()
    
    print("\n=== RS485 Port Tester ===\n")
    
    # Verfügbare Gerätetypen
    device_types = {
        '1': 'radar',
        '2': 'ph',
        '3': 'turbidity',
        '4': 'flow'
    }
    
    # Gerätetyp auswählen
    print("Verfügbare Gerätetypen:")
    for key, value in device_types.items():
        print(f"{key}: {value}")
    
    while True:
        device_choice = input("\nBitte wählen Sie den Gerätetyp (1-4): ").strip()
        if device_choice in device_types:
            device_type = device_types[device_choice]
            break
        print("Ungültige Auswahl!")

    # Geräte-ID eingeben
    while True:
        try:
            device_id = int(input("Bitte geben Sie die Geräte-ID ein (1-247): "))
            if 1 <= device_id <= 247:
                break
            print("ID muss zwischen 1 und 247 liegen!")
        except ValueError:
            print("Bitte geben Sie eine gültige Zahl ein!")

    # Port auswählen
    port = input("Bitte geben Sie den seriellen Port ein (Enter für /dev/ttyS0): ").strip()
    if not port:
        port = '/dev/ttyS0'

    # Testintervall
    while True:
        try:
            interval = float(input("Testintervall in Sekunden (Enter für 1.0): ").strip() or "1.0")
            if interval > 0:
                break
            print("Intervall muss größer als 0 sein!")
        except ValueError:
            print("Bitte geben Sie eine gültige Zahl ein!")

    # Starte Test
    tester = None
    try:
        print(f"\nInitialisiere Port {port}...")
        tester = RS485PortTester(port)
        tester.run_continuous_test(device_type, device_id, interval)
    except Exception as e:
        print(f"Kritischer Fehler: {e}")
    finally:
        if tester:
            tester.close()

if __name__ == "__main__":
    main() 