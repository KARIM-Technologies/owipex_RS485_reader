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

def test_radar_communication(device):
    """
    Testet die Kommunikation mit dem Radarsensor
    
    Returns:
        bool: True wenn erfolgreich, False wenn fehlgeschlagen
    """
    try:
        # Versuche einen Wert zu lesen
        value = device.read_radar_sensor(register_address=0x0001)
        if value is not None:
            logging.info(f"Kommunikationstest erfolgreich. Aktueller Messwert: {value}")
            return True
        else:
            logging.error("Kommunikationstest fehlgeschlagen: Keine Daten empfangen")
            return False
    except Exception as e:
        logging.error(f"Kommunikationstest fehlgeschlagen: {e}")
        return False

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
    dev_manager = None
    try:
        logging.info(f"Initialisiere Verbindung auf Port {port}...")
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
        logging.info(f"Verbinde mit Gerät auf Adresse {current_address}...")
        device = dev_manager.add_device(device_id=current_address)

        # Teste erst die Kommunikation
        logging.info("Teste Kommunikation mit dem Gerät...")
        if not test_radar_communication(device):
            logging.error("Konnte keine Verbindung zum Gerät herstellen")
            return False

        # Register für Geräteadresse ist 0x2000
        logging.info(f"Ändere Geräteadresse von {current_address} zu {new_address}...")
        device.write_registers(start_address=0x2000, values=[new_address])
        
        logging.info(f"Adressänderung durchgeführt. Warte 3 Sekunden...")
        time.sleep(3)  # Warte auf Reset des Geräts
        
        # Versuche mit der neuen Adresse zu kommunizieren
        logging.info(f"Versuche Verbindung mit neuer Adresse {new_address}...")
        dev_manager.remove_device(current_address)
        new_device = dev_manager.add_device(device_id=new_address)
        
        # Teste die Kommunikation mit der neuen Adresse
        if test_radar_communication(new_device):
            logging.info("Erfolgreich mit neuer Adresse verbunden!")
            return True
        else:
            logging.error("Konnte keine Verbindung mit neuer Adresse herstellen")
            return False

    except Exception as e:
        logging.error(f"Fehler beim Ändern der Geräteadresse: {e}")
        return False
    finally:
        if dev_manager is not None:
            # Schließe alle offenen Verbindungen im DeviceManager
            for device_id in dev_manager.devices:
                try:
                    dev_manager.devices[device_id].client.close()
                except:
                    pass

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