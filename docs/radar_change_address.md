# Anleitung: Ändern der Modbus-Adresse des Radarsensors

Diese Anleitung beschreibt, wie Sie die Modbus-Adresse eines Radarsensors mithilfe des `radar_address_changer.py` Skripts ändern können.

## Voraussetzungen

- Python 3.6 oder höher
- Physische RS485-Verbindung zum Radarsensor
- Administratorrechte auf dem System (für Zugriff auf serielle Ports)
- Installierte Python-Pakete:
  - `pymodbus`
  - `periphery`

## Technische Vorbereitung

### 1. Hardware-Setup
- RS485 zu USB Adapter oder direkte RS485-Schnittstelle
- Verkabelung:
  - A+ (RS485) → A+ (Sensor)
  - B- (RS485) → B- (Sensor)
  - GND → GND (optional, aber empfohlen)
- Stromversorgung des Sensors (12-24V DC)

### 2. Kommunikationseinstellungen
- Baudrate: 9600
- Datenbits: 8
- Stoppbits: 1
- Parität: None
- Modbus-RTU Protokoll

## Installation

1. Stellen Sie sicher, dass Sie sich im Hauptverzeichnis des Projekts befinden: