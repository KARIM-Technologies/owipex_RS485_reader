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
        self.last_read_times = {}  # Separate last read time for each sensor
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
                        'config': sensor_config,
                        'last_read': 0
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
                sensor_id: {
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
            sensor_data = sensor.read_data()
            
            if sensor_data:
                # Format data according to sensor configuration
                formatted_data = self.format_sensor_data(sensor_id, sensor_info, sensor_data)
                
                # Update simple and JSON data collections
                if 'simple' in formatted_data:
                    simple_data.update(formatted_data['simple'])
                if 'json' in formatted_data:
                    json_data.update(formatted_data['json'])
                
                # Update last read time
                sensor_info['last_read'] = current_time
        
        return {
            "simple": simple_data,
            "json": {
                "devices": json_data,
                "system_timestamp": int(current_time * 1000)
            }
        }
        
    def send_telemetry(self, data):
        """Send telemetry data to ThingsBoard"""
        if not self.client or not data:
            return

        try:
            if data.get("simple"):
                self.client.send_telemetry(data["simple"])
                logging.debug("Simple format telemetry sent successfully")
                
            if data.get("json"):
                self.client.send_telemetry({
                    "sensor_data": data["json"]
                })
                logging.debug("JSON format telemetry sent successfully")
                
            logging.info("All telemetry sent successfully")
        except Exception as e:
            logging.error(f"Error sending telemetry: {e}")
                
    def run(self):
        """Main run loop"""
        self.running = True
        while self.running:
            sensor_data = self.read_all_sensors()
            if sensor_data.get("simple") or sensor_data.get("json"):
                self.send_telemetry(sensor_data)
            time.sleep(1)  # Check every second
            
    def stop(self):
        """Stop the sensor manager"""
        self.running = False
        if self.client:
            self.client.disconnect()