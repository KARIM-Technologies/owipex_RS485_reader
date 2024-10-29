from .sensor_base import SensorBase

class RadarSensor(SensorBase):
    def __init__(self, device_id, device_manager):
        super().__init__(device_id, device_manager)
        
    def read_data(self):
        """Read radar sensor data"""
        try:
            # Using specific radar sensor reading method with unsigned short format
            measured_air_distance = self.device.read_radar_sensor(register_address=0x0001)
            
            if measured_air_distance is None:
                print("Error reading radar sensor")
                return None
                
            return {
                'measured_air_distance': measured_air_distance
            }
        except Exception as e:
            print(f"Error reading radar sensor: {e}")
            return None