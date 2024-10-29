from .sensor_base import SensorBase

class RadarSensor(SensorBase):
    def __init__(self, device_id, device_manager):
        super().__init__(device_id, device_manager)
        
    def read_data(self):
        """Read radar sensor data"""
        try:
            water_level = self.device.read_register(start_address=0x0001, register_count=2)
            return {
                'water_level': water_level
            }
        except Exception as e:
            print(f"Error reading radar sensor: {e}")
            return None