#!/usr/bin/env python3
import minimalmodbus
import serial
import time

class RadarSensorAddressChanger:
    def __init__(self, port='/dev/ttyUSB0', current_address=0x01):
        """
        Initialisiert den Radar-Sensor Address Changer
        
        Args:
            port: Serieller Port (default: /dev/ttyUSB0)
            current_address: Aktuelle Geräteadresse (default: 0x01)
        """
        self.instrument = minimalmodbus.Instrument(port, current_address)
        self.instrument.serial.baudrate = 9600
        self.instrument.serial.bytesize = 8
        self.instrument.serial.parity = serial.PARITY_NONE
        self.instrument.serial.stopbits = 1
        self.instrument.serial.timeout = 1
        self.instrument.mode = minimalmodbus.MODE_RTU

    def change_address(self, new_address):
        """
        Ändert die Geräteadresse des Radar-Sensors
        
        Args:
            new_address: Neue Geräteadresse (1-247)
        """
        if not 1 <= new_address <= 247:
            raise ValueError("Neue Adresse muss zwischen 1 und 247 liegen")
        
        try:
            # Register für Geräteadresse ist typischerweise 0x2000
            self.instrument.write_register(0x2000, new_address, 
                                        functioncode=0x10)
            print(f"Adresse erfolgreich von {self.instrument.address} "
                  f"zu {new_address} geändert")
            time.sleep(1)  # Warte auf Neustart des Geräts
            
        except Exception as e:
            print(f"Fehler beim Ändern der Adresse: {str(e)}")

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Radar-Sensor Adresse ändern')
    parser.add_argument('--port', default='/dev/ttyUSB0',
                       help='Serieller Port')
    parser.add_argument('--current-address', type=int, default=1,
                       help='Aktuelle Geräteadresse')
    parser.add_argument('--new-address', type=int, required=True,
                       help='Neue Geräteadresse (1-247)')
    
    args = parser.parse_args()
    
    changer = RadarSensorAddressChanger(
        port=args.port,
        current_address=args.current_address
    )
    
    changer.change_address(args.new_address)

if __name__ == "__main__":
    main() 