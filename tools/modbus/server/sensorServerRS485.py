import threading
from libs.modbus_lib import DeviceManager
import time  # Stelle sicher, dass time importiert ist

class SensorReader:
    def __init__(self, device_manager, sensor_configs, base_file_path="sensor_data"):
        self.device_manager = device_manager
        self.sensor_configs = sensor_configs
        self.base_file_path = base_file_path

    def start_reading(self):
        for config in self.sensor_configs:
            self.schedule_read(**config)

    def schedule_read(self, device_id, value_configs, interval, count, sensor_name):
        def read_and_save():
            values = {}
            for config in value_configs:
                read_values = []
                for _ in range(count):
                    try:
                        read_value = self.device_manager.get_device(device_id).read_register(config['register_address'], 2)
                        read_values.append(read_value)
                        time.sleep(1)  # Füge hier eine Pause von 1 Sekunde ein
                    except Exception as e:
                        print(f"Fehler beim Lesen von {sensor_name} (Geräte-ID {device_id}, Adresse {config['register_address']}): {e}")
                        continue
                if read_values:
                    avg_value = sum(read_values) / len(read_values)
                    values[config['value_name']] = avg_value
                
            if values:
                with open(f"{self.base_file_path}_{sensor_name}.txt", 'a') as file:
                    file.write(f"{sensor_name}: {values}\n")
            else:
                print(f"Warnung: Keine Werte für {sensor_name} zum Speichern verfügbar.")
            
            threading.Timer(interval, read_and_save).start()

        read_and_save()

# Konfiguration für Sensoren
sensor_configs = [
    {
        "device_id": 0x01,
        "value_configs": [
            {"register_address": 0x0000, "value_name": "Air_Height"},
            {"register_address": 0x0002, "value_name": "Liquid_Level"}
        ],
        "interval": 5,
        "count": 5,
        "sensor_name": "Radar_Sensor"
    },
    {
        "device_id": 0x02,
        "value_configs": [
            {"register_address": 0x0003, "value_name": "TempPHSens"},
            {"register_address": 0x0001, "value_name": "PHValue"}
        ],
        "interval": 20,
        "count": 5,
        "sensor_name": "PH_Sensor"
    },
    {
        "device_id": 0x03,
        "value_configs": [
            {"register_address": 0x0003, "value_name": "TempTruebSens"},
            {"register_address": 0x0001, "value_name": "TruebValue"}
        ],
        "interval": 20,
        "count": 5,
        "sensor_name": "Trub_Sensor"
    }
]

# DeviceManager-Erstellung und Konfiguration
dev_manager = DeviceManager(port='/dev/ttyS0', baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=1)
dev_manager.add_device(device_id=0x01)
dev_manager.add_device(device_id=0x02)
dev_manager.add_device(device_id=0x03)

# Starte das periodische Auslesen der Sensoren
reader = SensorReader(dev_manager, sensor_configs)
reader.start_reading()
