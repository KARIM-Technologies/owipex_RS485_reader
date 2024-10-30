from .sensor_base import SensorBase
import struct

class FlowSensor(SensorBase):
    def __init__(self, device_id, device_manager):
        super().__init__(device_id, device_manager)
        
    def read_float(self, start_address, byte_order='>'):
        """Read and convert two 16-bit registers to a 32-bit float."""
        value = self.device.read_register(start_address=start_address, register_count=2)
        return value  # The device manager already handles the conversion
    
    def read_long(self, start_address, byte_order='>'):
        """Read and convert two 16-bit registers to a 32-bit signed integer."""
        value = self.device.read_register(start_address=start_address, register_count=2)
        return int(value)  # Convert to integer for accumulator values
    
    def read_single(self, start_address):
        """Read a single 16-bit register."""
        value = self.device.read_register(start_address=start_address, register_count=1)
        return int(value)
    
    def read_data(self):
        """Read flow sensor data with proper scaling and byte order."""
        try:
            # Define the byte order based on your device's specification
            byte_order = '>'  # Try '>' for big-endian or '<' for little-endian

            # Read flow rate (m3/h) - 32-bit float
            flow_rate = self.read_float(0x0001, byte_order)
            
            # Read energy flow (kW) - 32-bit float
            energy_flow = self.read_float(0x0003, byte_order)
            
            # Read velocity (m/s) - 32-bit float
            velocity = self.read_float(0x0005, byte_order)
            
            # Read net flow accumulator - integer part (LONG)
            net_flow_int = self.read_long(0x0025, byte_order)
            
            # Read net flow decimal fraction - float
            net_flow_frac = self.read_float(0x0027, byte_order)
            
            # Read net flow decimal point adjustment (n)
            n = self.read_single(0x059F)
            if n > 32767:
                n -= 65536  # Convert to signed integer if necessary
            
            # Read unit from register 1438 (0x059E)
            unit_code = self.read_single(0x059E)
            units = {0: 'm³', 1: 'L', 2: 'GAL', 3: 'ft³'}
            unit = units.get(unit_code, 'unknown')
            
            # Calculate net flow with scaling
            net_flow = (net_flow_int + net_flow_frac) * (10 ** (n - 3))
            
            # Read temperatures (°C) - 32-bit float
            temp_supply = self.read_float(0x0033, byte_order)
            temp_return = self.read_float(0x0035, byte_order)
            
            return {
                'flow_rate': round(flow_rate, 3),       # m³/h
                'energy_flow': round(energy_flow, 3),   # kW
                'velocity': round(velocity, 3),         # m/s
                'net_flow': round(net_flow, 3),         # Adjusted for decimal point and unit
                'net_flow_unit': unit,
                'temp_supply': round(temp_supply, 2),   # °C
                'temp_return': round(temp_return, 2)    # °C
            }
            
        except Exception as e:
            print(f"Error reading flow sensor: {e}")
            return None