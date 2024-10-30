import struct
from .sensor_base import SensorBase

class FlowSensor(SensorBase):
    def __init__(self, device_id, device_manager):
        super().__init__(device_id, device_manager)
        
    def read_float(self, registers, byte_order='>'):
        """Convert two 16-bit registers to a 32-bit float."""
        if byte_order == '>':  # Big endian
            packed = struct.pack('>HH', *registers)
        elif byte_order == '<':  # Little endian
            packed = struct.pack('<HH', *registers)
        else:
            raise ValueError('Invalid byte order')
        return struct.unpack('>f', packed)[0]
    
    def read_long(self, registers, byte_order='>'):
        """Convert two 16-bit registers to a 32-bit signed integer."""
        if byte_order == '>':  # Big endian
            packed = struct.pack('>HH', *registers)
        elif byte_order == '<':  # Little endian
            packed = struct.pack('<HH', *registers)
        else:
            raise ValueError('Invalid byte order')
        return struct.unpack('>i', packed)[0]
    
    def read_data(self):
        """Read flow sensor data with proper scaling and byte order."""
        try:
            # Define the byte order based on your device's specification
            byte_order = '>'  # Try '>' for big-endian or '<' for little-endian

            # Read flow rate (m3/h) - 32-bit float
            flow_rate_regs = self.device.read_register(0x0001, 2)
            flow_rate = self.read_float(flow_rate_regs, byte_order)
            
            # Read energy flow (kW) - 32-bit float
            energy_flow_regs = self.device.read_register(0x0003, 2)
            energy_flow = self.read_float(energy_flow_regs, byte_order)
            
            # Read velocity (m/s) - 32-bit float
            velocity_regs = self.device.read_register(0x0005, 2)
            velocity = self.read_float(velocity_regs, byte_order)
            
            # Read net flow accumulator - integer part (LONG)
            net_flow_int_regs = self.device.read_register(0x0025, 2)
            net_flow_int = self.read_long(net_flow_int_regs, byte_order)
            
            # Read net flow decimal fraction - float
            net_flow_frac_regs = self.device.read_register(0x0027, 2)
            net_flow_frac = self.read_float(net_flow_frac_regs, byte_order)
            
            # Read net flow decimal point adjustment (n)
            n_reg = self.device.read_register(0x059F, 1)
            n = n_reg[0]
            if n > 32767:
                n -= 65536  # Convert to signed integer if necessary
            
            # Read unit from register 1438 (0x059E)
            unit_reg = self.device.read_register(0x059E, 1)
            unit_code = unit_reg[0]
            units = {0: 'm³', 1: 'L', 2: 'GAL', 3: 'ft³'}
            unit = units.get(unit_code, 'unknown')
            
            # Calculate net flow with scaling
            net_flow = (net_flow_int + net_flow_frac) * (10 ** (n - 3))
            
            # Read temperatures (°C) - 32-bit float
            temp_supply_regs = self.device.read_register(0x0033, 2)
            temp_supply = self.read_float(temp_supply_regs, byte_order)
            
            temp_return_regs = self.device.read_register(0x0035, 2)
            temp_return = self.read_float(temp_return_regs, byte_order)
            
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