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
        
        # Send initial sensor configuration
        self.send_sensor_config()

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
        
    def send_sensor_config(self):
        """Send sensor configuration as attributes to ThingsBoard"""
        if self.client:
            try:
                config_data = {
                    sensor_id: {
                        'name': info['config']['name'],
                        'location': info['config']['location'],
                        'type': info['config']['type'],
                        'device_id': info['config']['device_id']
                    }
                    for sensor_id, info in self.sensors.items()
                }
                self.client.send_attributes({'sensors': config_data})
                logging.info("Sensor configuration sent successfully")
            except Exception as e:
                logging.error(f"Error sending sensor configuration: {e}")
        
    def read_all_sensors(self):
        """Read data from all sensors"""
        data = {}
        for sensor_id, sensor_info in self.sensors.items():
            sensor = sensor_info['sensor']
            sensor_data = sensor.read_data()
            
            if sensor_data:
                # Keep the original format for sensor readings
                data.update({f"{sensor_id}_{k}": v for k, v in sensor_data.items()})
                
        return data
        
    def send_telemetry(self, data):
        """Send telemetry data to ThingsBoard"""
        if self.client and data:
            try:
                self.client.send_telemetry(data)
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