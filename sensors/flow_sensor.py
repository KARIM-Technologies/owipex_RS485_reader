from .sensor_base import SensorBase
import time

class FlowSensor(SensorBase):
    def __init__(self, device_id, device_manager):
        super().__init__(device_id, device_manager)
        self.logger.info(f"FlowSensor {device_id} initialisiert")
        
    def read_data(self):
        """Read flow sensor data"""
        try:
            # Längere Wartezeit vor dem ersten Lesen
            time.sleep(0.5)
            
            # Read flow rate first (most important value)
            flow_rate = self.device.read_flow_sensor(0x0001)
            if flow_rate is None:
                self.logger.error(f"Konnte flow_rate nicht lesen von Sensor {self.device_id}")
                return None
                
            # Längere Wartezeit zwischen den Lesevorgängen
            time.sleep(0.3)
            
            # Read velocity
            velocity = self.device.read_flow_sensor(0x0005)
            if velocity is None:
                velocity = 0.0
                
            time.sleep(0.3)
            
            # Read temperatures
            temp_supply = self.device.read_flow_sensor(0x0033)
            if temp_supply is None:
                temp_supply = 0.0
                
            time.sleep(0.3)
            
            temp_return = self.device.read_flow_sensor(0x0035)
            if temp_return is None:
                temp_return = 0.0
                
            time.sleep(0.3)
            
            # Read flow accumulator integer part only (32-bit LONG)
            flow_int_low = self.device.read_register(0x0009)
            flow_int_high = self.device.read_register(0x0010)
            
            if flow_int_low is not None and flow_int_high is not None:
                flow_integer = (flow_int_high << 16) | flow_int_low
            else:
                flow_integer = 0
                
            time.sleep(0.3)
            
            # Read unit and decimal point configuration with default values
            try:
                flow_unit = self.device.read_register(0x1438) or 0  # Default to m3
                flow_decimal_point = self.device.read_register(0x1439) or 3  # Default scaling
            except:
                flow_unit = 0
                flow_decimal_point = 3
            
            # Calculate total flow with correct scaling
            total_flow = flow_integer * (10 ** (flow_decimal_point - 3))
            
            time.sleep(0.3)
            
            # Read energy accumulator integer part only
            try:
                energy_int_low = self.device.read_register(0x0013)
                energy_int_high = self.device.read_register(0x0014)
                energy_integer = (energy_int_high << 16) | energy_int_low if energy_int_low is not None and energy_int_high is not None else 0
            except:
                energy_integer = 0
            
            time.sleep(0.3)
            
            # Read energy configuration with default values
            try:
                energy_decimal_point = self.device.read_register(0x1440) or 4  # Default scaling
                energy_unit = self.device.read_register(0x1441) or 0  # Default unit
            except:
                energy_decimal_point = 4
                energy_unit = 0
            
            # Calculate total energy with correct scaling
            total_energy = energy_integer * (10 ** (energy_decimal_point - 4))
            
            # Map flow unit to string representation
            flow_unit_map = {0: 'm³', 1: 'L', 2: 'GAL', 3: 'CF'}
            flow_unit_str = flow_unit_map.get(flow_unit, 'm³')
            
            self.logger.debug(f"Erfolgreich gelesen - Flow Sensor {self.device_id}: flow_rate={flow_rate}")
            
            return {
                'flow_rate': flow_rate,
                'velocity': velocity,
                'temp_supply': temp_supply,
                'temp_return': temp_return,
                'total_flow': total_flow,
                'total_flow_unit': flow_unit_str,
                'total_energy': total_energy,
                'flow_decimal_point': flow_decimal_point,
                'energy_decimal_point': energy_decimal_point
            }
        except Exception as e:
            self.logger.error(f"Fehler beim Lesen von Flow Sensor {self.device_id}: {e}")
            return None