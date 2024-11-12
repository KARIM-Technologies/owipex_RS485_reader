import os
import time
import json
import logging
from dotenv import load_dotenv
from tb_gateway_mqtt import TBDeviceMqttClient
from modbus_manager import DeviceManager
from .ph_sensor import PHSensor
from .turbidity_sensor import TurbiditySensor
from .flow_sensor import FlowSensor
from .radar_sensor import RadarSensor

class SensorManager:
    def __init__(self, config_path='config/sensors.json'):
        # Load environment variables
        load_dotenv(dotenv_path='/etc/owipex/.envRS485')
        
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s'
        )
        self.logger = logging.getLogger('SensorManager')
        
        self.logger.info("Initialisiere SensorManager...")
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Initialize Modbus connection with settings from config
        rs485_settings = self.config.get('rs485_settings', {})
        self.logger.info("Stelle Modbus-Verbindung her...")
        self.dev_manager = DeviceManager(
            port=rs485_settings.get('port', '/dev/ttyS0'),
            baudrate=rs485_settings.get('baudrate', 9600),
            parity=rs485_settings.get('parity', 'N'),
            stopbits=rs485_settings.get('stopbits', 1),
            bytesize=rs485_settings.get('bytesize', 8),
            timeout=rs485_settings.get('timeout', 1)
        )
        
        # Load sensor configuration
        self.sensors = self.load_sensors(self.config.get('sensors', []))
        
        # Initialize ThingsBoard connection
        self.client = None
        self.running = False
        self.last_read_times = {}
        self.READ_INTERVAL = int(os.environ.get('RS485_READ_INTERVAL', 15))
        self.logger.info(f"Read Interval: {self.READ_INTERVAL} Sekunden")

    def load_sensors(self, sensor_configs):
        """Load sensor configuration from config"""
        sensors = {}
        sensor_classes = {
            'ph': PHSensor,
            'turbidity': TurbiditySensor,
            'flow': FlowSensor,
            'radar': RadarSensor
        }
        
        for sensor_config in sensor_configs:
            sensor_type = sensor_config['type']
            sensor_id = sensor_config['id']
            device_id = sensor_config['device_id']
            
            self.logger.info(f"Konfiguriere Sensor: {sensor_id} (Typ: {sensor_type}, Device ID: {device_id})")
            
            if sensor_type in sensor_classes:
                sensor_class = sensor_classes[sensor_type]
                sensor = sensor_class(
                    device_id=device_id,
                    device_manager=self.dev_manager
                )
                sensors[sensor_id] = {
                    'sensor': sensor,
                    'config': sensor_config,
                    'last_read': 0
                }
                self.logger.info(f"Sensor {sensor_id} erfolgreich initialisiert")
            else:
                self.logger.warning(f"Unbekannter Sensor-Typ: {sensor_type}")
        
        self.logger.info(f"Insgesamt {len(sensors)} Sensoren geladen")
        return sensors

    def connect_to_server(self):
        """Connect to ThingsBoard server"""
        access_token = os.environ.get('RS485_ACCESS_TOKEN')
        if not access_token:
            self.logger.error("RS485_ACCESS_TOKEN nicht gefunden in .envRS485")
            raise ValueError("RS485_ACCESS_TOKEN not found in .envRS485")
            
        server = os.environ.get('RS485_THINGSBOARD_SERVER', 'localhost')
        port = int(os.environ.get('RS485_THINGSBOARD_PORT', 1883))
        
        self.logger.info(f"Verbinde mit ThingsBoard Server: {server}:{port}")
        self.client = TBDeviceMqttClient(server, port, access_token)
        self.client.connect()
        self.logger.info("Erfolgreich mit ThingsBoard verbunden")

    def format_sensor_data(self, sensor_id, sensor_info, sensor_data):
        """Format sensor data according to configuration"""
        config = sensor_info['config']
        formats = config['transmission']['formats']
        formatted_data = {}

        if 'simple' in formats:
            # Einfaches Format (key-value Paare)
            formatted_data['simple'] = {
                f"{sensor_id}_{k}": v for k, v in sensor_data.items()
            }

        if 'json' in formats:
            # JSON Format mit Metadaten
            formatted_data['json'] = {
                f"{sensor_id}_data": {
                    "info": {
                        "name": config['name'],
                        "location": config['location'],
                        "type": config['type'],
                        "device_id": config['device_id']
                    },
                    "metadata": config['metadata'],
                    "measurements": sensor_data,
                    "timestamp": int(time.time() * 1000),
                    "status": "active"
                }
            }

        return formatted_data

    def should_read_sensor(self, sensor_info):
        """Check if sensor should be read based on its interval"""
        current_time = time.time()
        interval = sensor_info['config']['transmission']['interval']
        last_read = sensor_info['last_read']
        
        return (current_time - last_read) >= interval

    def read_all_sensors(self):
        """Read data from all sensors"""
        simple_data = {}
        json_data = {}
        current_time = time.time()
        
        for sensor_id, sensor_info in self.sensors.items():
            if not self.should_read_sensor(sensor_info):
                continue

            sensor = sensor_info['sensor']
            self.logger.debug(f"Lese Sensor {sensor_id}...")
            
            try:
                sensor_data = sensor.read_data()
                
                if sensor_data:
                    self.logger.info(f"Sensor {sensor_id} erfolgreich gelesen: {sensor_data}")
                    # Format data according to sensor configuration
                    formatted_data = self.format_sensor_data(sensor_id, sensor_info, sensor_data)
                    
                    # Update simple and JSON data collections
                    if 'simple' in formatted_data:
                        simple_data.update(formatted_data['simple'])
                    if 'json' in formatted_data:
                        json_data.update(formatted_data['json'])
                    
                    # Update last read time
                    sensor_info['last_read'] = current_time
                else:
                    self.logger.error(f"Keine Daten von Sensor {sensor_id} erhalten")
            except Exception as e:
                self.logger.error(f"Fehler beim Lesen von Sensor {sensor_id}: {e}")
        
        return {
            "simple": simple_data,
            "json": json_data
        }
        
    def send_telemetry(self, data):
        """Send telemetry data to ThingsBoard"""
        if not self.client or not data:
            return

        try:
            # Sende Simple-Format Daten
            if data.get("simple"):
                self.client.send_telemetry(data["simple"])
                self.logger.debug("Simple format Telemetrie erfolgreich gesendet")
                
            # Sende JSON-Format Daten - jetzt einzeln pro Sensor
            if data.get("json"):
                for sensor_data_key, sensor_data in data["json"].items():
                    self.client.send_telemetry({
                        sensor_data_key: sensor_data
                    })
                    self.logger.debug(f"JSON format Telemetrie für {sensor_data_key} erfolgreich gesendet")
                
            self.logger.info("Alle Telemetrie-Daten erfolgreich gesendet")
        except Exception as e:
            self.logger.error(f"Fehler beim Senden der Telemetrie: {e}")
                
    def run(self):
        """Main run loop"""
        self.logger.info("Starte SensorManager...")
        self.running = True
        while self.running:
            current_time = time.time()
            
            # Prüfe jeden Sensor
            for sensor_id, sensor_info in self.sensors.items():
                if self.should_read_sensor(sensor_info):
                    self.logger.debug(f"Lese Sensor {sensor_id}...")
                    try:
                        sensor_data = sensor_info['sensor'].read_data()
                        if sensor_data:
                            self.logger.info(f"Sensor {sensor_id} erfolgreich gelesen: {sensor_data}")
                            formatted_data = self.format_sensor_data(sensor_id, sensor_info, sensor_data)
                            self.send_telemetry(formatted_data)
                            sensor_info['last_read'] = current_time
                        else:
                            self.logger.error(f"Keine Daten von Sensor {sensor_id} erhalten")
                    except Exception as e:
                        self.logger.error(f"Fehler beim Lesen von Sensor {sensor_id}: {e}")
            
            # Warte eine Sekunde vor der nächsten Prüfung
            time.sleep(1)
            
    def stop(self):
        """Stop the sensor manager"""
        self.logger.info("Stoppe SensorManager...")
        self.running = False
        if self.client:
            self.client.disconnect()
        self.logger.info("SensorManager gestoppt")