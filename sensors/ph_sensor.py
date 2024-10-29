from .sensor_base import SensorBase

class PHSensor(SensorBase):
    def __init__(self, device_id, device_manager):
        super().__init__(device_id, device_manager)
        
    def read_data(self):
        """Read pH sensor data"""
        try:
            ph_value = self.device.read_register(start_address=0x0001, register_count=2)
            temperature = self.device.read_register(start_address=0x0003, register_count=2)
            return {
                'ph_value': ph_value,
                'temperature': temperature
            }
        except Exception as e:
            print(f"Error reading pH sensor: {e}")
            return None