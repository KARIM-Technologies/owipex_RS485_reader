from .sensor_base import SensorBase

class TurbiditySensor(SensorBase):
    def __init__(self, device_id, device_manager):
        super().__init__(device_id, device_manager)
        
    def read_data(self):
        """Read turbidity sensor data"""
        try:
            turbidity = self.device.read_register(start_address=0x0001, register_count=2)
            temperature = self.device.read_register(start_address=0x0003, register_count=2)
            return {
                'turbidity': turbidity,
                'temperature': temperature
            }
        except Exception as e:
            print(f"Error reading turbidity sensor: {e}")
            return None