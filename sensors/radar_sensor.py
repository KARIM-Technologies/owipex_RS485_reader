from .sensor_base import SensorBase

class RadarSensor(SensorBase):
    def __init__(self, device_id, device_manager):
        super().__init__(device_id, device_manager)
        
    def read_data(self):
        """Read radar sensor data"""
        try:
            # Using the same format as in the original sensor_reader.py
            water_level = self.device.read_register(
                start_address=0x0001, 
                register_count=2, 
                data_format='>f'  # Big-endian float format
            )
            
            return {
                'water_level': round(water_level, 2)  # Round to 2 decimal places for consistency
            }
        except Exception as e:
            print(f"Error reading radar sensor: {e}")
            return None