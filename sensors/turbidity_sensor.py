from .sensor_base import SensorBase

class TurbiditySensor(SensorBase):
    def __init__(self, device_id, device_manager):
        super().__init__(device_id, device_manager)
        
    def read_data(self):
        """Read turbidity sensor data"""
        try:
            # Lese Trübung (Register 0x0001, 2 Register)
            turbidity = self.device.read_register(start_address=0x0001, register_count=2)
            if turbidity is None:
                self.logger.error(f"Fehler beim Lesen der Trübung von Gerät {self.device_id}")
                return None
                
            # Lese Temperatur (Register 0x0003, 2 Register)
            temperature = self.device.read_register(start_address=0x0003, register_count=2)
            if temperature is None:
                self.logger.error(f"Fehler beim Lesen der Temperatur von Gerät {self.device_id}")
                return None
                
            self.logger.debug(f"Trübung: {turbidity}, Temperatur: {temperature}")
            return {
                'turbidity': turbidity,
                'temperature': temperature
            }
        except Exception as e:
            self.logger.error(f"Fehler beim Lesen des Trübungssensors (ID: {self.device_id}): {str(e)}")
            return None