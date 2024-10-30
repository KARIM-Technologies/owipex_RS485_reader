from .sensor_base import SensorBase

class FlowSensor(SensorBase):
    def __init__(self, device_id, device_manager):
        super().__init__(device_id, device_manager)
        
    def read_data(self):
        """Read flow sensor data"""
        try:
            # Read flow accumulator integer part only (32-bit LONG)
            flow_int_low = self.device.read_register(0x0009)
            flow_int_high = self.device.read_register(0x0010)
            
            if flow_int_low is None or flow_int_high is None:
                print("Error reading flow integer values")
                return None
                
            flow_integer = (flow_int_high << 16) | flow_int_low
            
            # Read unit and decimal point configuration with default values
            flow_unit = self.device.read_register(0x1438) or 0  # Default to m3
            flow_decimal_point = self.device.read_register(0x1439) or 3  # Default scaling
            
            # Calculate total flow with correct scaling
            total_flow = flow_integer * (10 ** (flow_decimal_point - 3))
            
            # Read energy accumulator integer part only
            energy_int_low = self.device.read_register(0x0013)
            energy_int_high = self.device.read_register(0x0014)
            
            if energy_int_low is None or energy_int_high is None:
                print("Error reading energy integer values")
                return None
                
            energy_integer = (energy_int_high << 16) | energy_int_low
            
            # Read energy configuration with default values
            energy_decimal_point = self.device.read_register(0x1440) or 4  # Default scaling
            energy_unit = self.device.read_register(0x1441) or 0  # Default unit
            
            # Calculate total energy with correct scaling
            total_energy = energy_integer * (10 ** (energy_decimal_point - 4))
            
            # Read other sensor values
            flow_rate = self.device.read_flow_sensor(0x0001) or 0.0  # m3/h
            velocity = self.device.read_flow_sensor(0x0005) or 0.0  # m/s
            temp_supply = self.device.read_flow_sensor(0x0033) or 0.0  # °C
            temp_return = self.device.read_flow_sensor(0x0035) or 0.0  # °C
            
            # Map flow unit to string representation
            flow_unit_map = {0: 'm³', 1: 'L', 2: 'GAL', 3: 'CF'}
            flow_unit_str = flow_unit_map.get(flow_unit, 'm³')
            
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
            print(f"Error reading flow sensor: {e}")
            return None