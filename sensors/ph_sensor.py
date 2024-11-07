from .sensor_base import SensorBase
import struct

class PHSensor(SensorBase):
    def __init__(self, device_id, device_manager):
        super().__init__(device_id, device_manager)
        
    def read_data(self):
        """Read pH sensor data"""
        try:
            # Lese Rohdaten für PH-Wert
            raw_ph = self.device.read_register(start_address=0x0001, register_count=2)
            if raw_ph is None:
                self.logger.error(f"Fehler beim Lesen des PH-Werts von Gerät {self.device_id}")
                return None
                
            # Lese Rohdaten für Temperatur
            raw_temp = self.device.read_register(start_address=0x0003, register_count=2)
            if raw_temp is None:
                self.logger.error(f"Fehler beim Lesen der Temperatur von Gerät {self.device_id}")
                return None
            
            # Konvertiere die Rohdaten in Float-Werte
            try:
                ph_bytes = struct.pack('>HH', raw_ph >> 16, raw_ph & 0xFFFF)
                temp_bytes = struct.pack('>HH', raw_temp >> 16, raw_temp & 0xFFFF)
                
                ph_value = struct.unpack('>f', ph_bytes)[0]
                temperature = struct.unpack('>f', temp_bytes)[0]
                
                self.logger.debug(f"PH-Wert: {ph_value}, Temperatur: {temperature}")
                return {
                    'ph_value': ph_value,
                    'temperature': temperature
                }
            except struct.error as e:
                self.logger.error(f"Fehler bei der Konvertierung der Daten: {e}")
                return None
                
        except Exception as e:
            self.logger.error(f"Fehler beim Lesen des PH-Sensors (ID: {self.device_id}): {str(e)}")
            return None