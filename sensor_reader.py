import sys
import logging
import time
import json
import threading
from periphery import GPIO
from tb_gateway_mqtt import TBDeviceMqttClient
from dotenv import load_dotenv
import os
from modbus_manager import DeviceManager

# Load environment variables from dedicated RS485 config
load_dotenv(dotenv_path='/etc/owipex/.envRS485')
ACCESS_TOKEN = os.environ.get('RS485_ACCESS_TOKEN')
THINGSBOARD_SERVER = os.environ.get('RS485_THINGSBOARD_SERVER', 'localhost')
THINGSBOARD_PORT = int(os.environ.get('RS485_THINGSBOARD_PORT', 1883))

class SensorReader:
    def __init__(self, port='/dev/ttyS0', baudrate=9600):
        self.dev_manager = DeviceManager(
            port=port, 
            baudrate=baudrate,
            parity='N',
            stopbits=1,
            bytesize=8,
            timeout=1
        )
        # Initialize sensors
        self.radar_sensor = self.dev_manager.add_device(device_id=0x01)
        self.turbidity_sensor = self.dev_manager.add_device(device_id=0x02)
        self.ph_sensor = self.dev_manager.add_device(device_id=0x03)
        
        self.client = None
        self.running = False
        self.last_read_time = 0
        self.READ_INTERVAL = int(os.environ.get('RS485_READ_INTERVAL', 15))  # seconds

    def connect_to_server(self):
        if not ACCESS_TOKEN:
            raise ValueError("RS485_ACCESS_TOKEN not found in .envRS485")
        self.client = TBDeviceMqttClient(THINGSBOARD_SERVER, THINGSBOARD_PORT, ACCESS_TOKEN)
        self.client.connect()
        
    def read_sensors(self):
        try:
            # Read PH sensor
            ph_value = self.ph_sensor.read_register(start_address=0x0001, register_count=2)
            ph_temp = self.ph_sensor.read_register(start_address=0x0003, register_count=2)
            
            # Read Turbidity sensor
            turbidity = self.turbidity_sensor.read_register(start_address=0x0001, register_count=2)
            turb_temp = self.turbidity_sensor.read_register(start_address=0x0003, register_count=2)
            
            # Read Radar sensor
            water_level = self.radar_sensor.read_register(start_address=0x0001, register_count=2)
            
            return {
                'ph_value': ph_value,
                'ph_temperature': ph_temp,
                'turbidity': turbidity,
                'turbidity_temperature': turb_temp,
                'water_level': water_level
            }
        except Exception as e:
            logging.error(f"Error reading sensors: {e}")
            return None

    def send_telemetry(self, data):
        if self.client and data:
            try:
                self.client.send_telemetry(data)
                logging.info("Telemetry sent successfully")
            except Exception as e:
                logging.error(f"Error sending telemetry: {e}")

    def run(self):
        self.running = True
        while self.running:
            current_time = time.time()
            if current_time - self.last_read_time >= self.READ_INTERVAL:
                sensor_data = self.read_sensors()
                if sensor_data:
                    self.send_telemetry(sensor_data)
                self.last_read_time = current_time
            time.sleep(1)

    def stop(self):
        self.running = False
        if self.client:
            self.client.disconnect()

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    sensor_reader = SensorReader()
    try:
        sensor_reader.connect_to_server()
        sensor_reader.run()
    except KeyboardInterrupt:
        logging.info("Shutting down...")
        sensor_reader.stop()
    except Exception as e:
        logging.error(f"Error: {e}")
        sensor_reader.stop()

if __name__ == "__main__":
    main()