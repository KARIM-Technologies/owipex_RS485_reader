from .sensor_base import SensorBase

class RadarSensor(SensorBase):
    def __init__(self, device_id, device_manager):
        super().__init__(device_id, device_manager)
        
    def read_data(self):
        """Read radar sensor data"""
        try:
            # Lese Füllstand (Register 0x0001)
            measured_air_distance = self.device.read_radar_sensor(register_address=0x0001)
            
            if measured_air_distance is None:
                self.logger.error(f"Fehler beim Lesen des Füllstands von Gerät {self.device_id}")
                return None
                
            self.logger.debug(f"Gemessene Luftstrecke: {measured_air_distance}")
            return {
                'measured_air_distance': measured_air_distance
            }
        except Exception as e:
            self.logger.error(f"Fehler beim Lesen des Radarsensors (ID: {self.device_id}): {str(e)}")
            return None