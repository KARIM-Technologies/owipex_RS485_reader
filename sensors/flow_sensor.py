from .sensor_base import SensorBase
import time
import logging

class FlowSensor(SensorBase):
    def __init__(self, device_id, device_manager):
        super().__init__(device_id, device_manager)
        self.logger = logging.getLogger(f'Sensor_FlowSensor_{device_id}')
        self.logger.info(f"FlowSensor {device_id} initialisiert")
        
    def read_data(self):
        """Read flow sensor data"""
        try:
            # Nur die wichtigsten Werte lesen
            flow_rate = self.device.read_flow_sensor(0x0001)
            if flow_rate is None:
                self.logger.error(f"Konnte flow_rate nicht lesen von Sensor {self.device_id}")
                return None
                
            time.sleep(0.1)
            
            velocity = self.device.read_flow_sensor(0x0005) or 0.0
            
            self.logger.debug(f"Erfolgreich gelesen - Flow Sensor {self.device_id}: flow_rate={flow_rate}")
            
            return {
                'flow_rate': flow_rate,
                'velocity': velocity
            }
            
        except Exception as e:
            self.logger.error(f"Fehler beim Lesen von Flow Sensor {self.device_id}: {e}")
            return None