#!/usr/bin/env python3
import sys
import os
import argparse
import logging
import time

# Füge den Hauptverzeichnispfad zum Python-Path hinzu
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from modbus_manager import DeviceManager

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def change_radar_address(port: str, current_address: int, new_address: int) -> bool:
    """
    Ändert die Modbus-Adresse des Radarsensors.
    
    Args:
        port: Der serielle Port (z.B. '/dev/ttyS0')
        current_address: Aktuelle Geräteadresse (Standard: 0x01)
        new_address: Neue gewünschte Geräteadresse (1-247)
    
    Returns:
        bool: True wenn erfolgreich, False wenn fehlgeschlagen
    """
    try:
        # Initialisiere ModbusManager mit Standard-Einstellungen
        dev_manager = DeviceManager(
            port=port,
            baudrate=9600,
            parity='N',
            stopbits=1,
            bytesize=8,
            timeout=1
        )

        # Verbinde mit dem Gerät unter der aktuellen Adresse
        device = dev_manager.add_device(device_id=current_address)

        # Register für Geräteadresse ist typischerweise 0x2000
        # Schreibe neue Adresse
        device.write_register(start_address=0x2000, values=[new_address])
        
        logging.info(f"Adressänderung durchgeführt. Warte 3 Sekunden...")
        time.sleep(3)  # Warte auf Reset des Geräts
        
        # Versuche mit der neuen Adresse zu kommunizieren
        dev_manager.remove_device(current_address)
        new_device = dev_manager.add_device(device_id=new_address)
        
        # Teste die Kommunikation
        test_read = new_device.read_register(start_address=0x0001, register_count=1)
        logging.info(f"Erfolgreich mit neuer Adresse verbunden. Test-Lesung: {test_read}")
        
        return True

    except Exception as e:
        logging.error(f"Fehler beim Ändern der Geräteadresse: {e}")
        return False
    finally:
        dev_manager.close()

def main():
    setup_logging()
    
    parser = argparse.ArgumentParser(description='Radar Sensor Adress Changer')
    parser.add_argument('--port', type=str, default='/dev/ttyS0',
                      help='Serieller Port (Standard: /dev/ttyS0)')
    parser.add_argument('--current-address', type=int, default=1,
                      help='Aktuelle Geräteadresse (Standard: 1)')
    parser.add_argument('--new-address', type=int, required=True,
                      help='Neue Geräteadresse (1-247)')

    args = parser.parse_args()

    # Validiere Eingaben
    if not 1 <= args.new_address <= 247:
        logging.error("Neue Adresse muss zwischen 1 und 247 liegen!")
        sys.exit(1)

    # Sicherheitsabfrage
    confirm = input(f"WARNUNG: Möchten Sie die Geräteadresse wirklich von {args.current_address} "
                   f"zu {args.new_address} ändern? (j/N): ")
    
    if confirm.lower() != 'j':
        logging.info("Adressänderung abgebrochen.")
        sys.exit(0)

    if change_radar_address(args.port, args.current_address, args.new_address):
        logging.info("Adressänderung erfolgreich abgeschlossen!")
    else:
        logging.error("Adressänderung fehlgeschlagen!")
        sys.exit(1)

if __name__ == "__main__":
    main() 