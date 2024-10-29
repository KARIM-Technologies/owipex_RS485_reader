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
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Initialize Modbus connection
        self.dev_manager = DeviceManager(
            port='/dev/ttyS0',
            baudrate=9600,
            parity='N',
            stopbits=1,
            bytesize=8,
            timeout=1
        )
        
        # Load sensor configuration
        self.sensors = self.load_sensors(config_path)
        
        # Initialize ThingsBoard connection
        self.client = None
        self.running = False
        self.last_read_time = 0
        self.READ_INTERVAL = int(os.environ.get('RS485_READ_INTERVAL', 15))

    def load_sensors(self, config_path):
        """Load sensor configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            sensors = {}
            sensor_classes = {
                'ph': PHSensor,
                'turbidity': TurbiditySensor,
                'flow': FlowSensor,
                'radar': RadarSensor
            }
            
            for sensor_config in config['sensors']:
                sensor_type = sensor_config['type']
                if sensor_type in sensor_classes:
                    sensor_class = sensor_classes[sensor_type]
                    sensor = sensor_class(
                        device_id=sensor_config['device_id'],
                        device_manager=self.dev_manager
                    )
                    sensors[sensor_config['id']] = {
                        'sensor': sensor,
                        'config': sensor_config
                    }
                else:
                    logging.warning(f"Unknown sensor type: {sensor_type}")
            
            return sensors
        except Exception as e:
            logging.error(f"Error loading sensor configuration: {e}")
            raise
        
    def connect_to_server(self):
        """Connect to ThingsBoard server"""
        access_token = os.environ.get('RS485_ACCESS_TOKEN')
        if not access_token:
            raise ValueError("RS485_ACCESS_TOKEN not found in .envRS485")
            
        server = os.environ.get('RS485_THINGSBOARD_SERVER', 'localhost')
        port = int(os.environ.get('RS485_THINGSBOARD_PORT', 1883))
        
        self.client = TBDeviceMqttClient(server, port, access_token)
        self.client.connect()
        
    def read_all_sensors(self):
        """Read data from all sensors"""
        simple_data = {}  # Flaches Format für einfache Abfragen
        detailed_data = {  # Detailliertes Format mit allen Informationen
            "devices": {},
            "timestamp": int(time.time() * 1000)  # Millisekunden seit Epoch
        }
        
        for sensor_id, sensor_info in self.sensors.items():
            sensor = sensor_info['sensor']
            config = sensor_info['config']
            sensor_data = sensor.read_data()
            
            if sensor_data:
                # Einfaches Format
                for k, v in sensor_data.items():
                    simple_data[f"{sensor_id}_{k}"] = v
                
                # Detailliertes Format
                detailed_data["devices"][sensor_id] = {
                    "info": {
                        "name": config['name'],
                        "location": config['location'],
                        "type": config['type'],
                        "device_id": config['device_id']
                    },
                    "measurements": sensor_data,
                    "status": "active"
                }
        
        return {
            "simple": simple_data,
            "detailed": detailed_data
        }
        
    def send_telemetry(self, data):
        """Send telemetry data to ThingsBoard"""
        if self.client and data:
            try:
                # Sende beide Datenformate
                self.client.send_telemetry(data["simple"])  # Einfaches Format für schnelle Abfragen
                self.client.send_telemetry({
                    "sensor_data": data["detailed"]  # Detailliertes Format unter eigenem Key
                })
                logging.info("Telemetry sent successfully")
            except Exception as e:
                logging.error(f"Error sending telemetry: {e}")
                
    def run(self):
        """Main run loop"""
        self.running = True
        while self.running:
            current_time = time.time()
            if current_time - self.last_read_time >= self.READ_INTERVAL:
                sensor_data = self.read_all_sensors()
                if sensor_data:
                    self.send_telemetry(sensor_data)
                self.last_read_time = current_time
            time.sleep(1)
            
    def stop(self):
        """Stop the sensor manager"""
        self.running = False
        if self.client:
            self.client.disconnect()