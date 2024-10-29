import os
import time
import logging
from dotenv import load_dotenv
from tb_gateway_mqtt import TBDeviceMqttClient
from modbus_manager import DeviceManager
from .ph_sensor import PHSensor
from .turbidity_sensor import TurbiditySensor
from .flow_sensor import FlowSensor
from .radar_sensor import RadarSensor

class SensorManager:
    def __init__(self):
        # Load environment variables from .envRS485
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
        
        # Initialize sensors
        self.sensors = {
            'radar': RadarSensor(0x01, self.dev_manager),
            'turbidity': TurbiditySensor(0x02, self.dev_manager),
            'ph': PHSensor(0x03, self.dev_manager),
            'flow': FlowSensor(0x04, self.dev_manager)
        }
        
        # Initialize ThingsBoard connection
        self.client = None
        self.running = False
        self.last_read_time = 0
        self.READ_INTERVAL = int(os.environ.get('RS485_READ_INTERVAL', 15))
        
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
        data = {}
        for sensor_name, sensor in self.sensors.items():
            sensor_data = sensor.read_data()
            if sensor_data:
                data.update({f"{sensor_name}_{k}": v for k, v in sensor_data.items()})
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