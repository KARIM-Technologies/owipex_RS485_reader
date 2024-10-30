from .sensor_base import SensorBase

class FlowSensor(SensorBase):
    def __init__(self, device_id, device_manager):
        super().__init__(device_id, device_manager)
        
    def read_data(self):
        """Read flow sensor data with proper formatting"""
        try:
            # Read flow rate (m3/h) - IEEE754 format
            flow_rate = self.device.read_register(
                start_address=0x0001, 
                register_count=2,
                data_format='>f'  # IEEE754 big-endian float
            )
            
            # Read energy flow (kW) - IEEE754 format
            energy_flow = self.device.read_register(
                start_address=0x0003, 
                register_count=2,
                data_format='>f'
            )
            
            # Read velocity (m/s) - IEEE754 format
            velocity = self.device.read_register(
                start_address=0x0005, 
                register_count=2,
                data_format='>f'
            )
            
            # Read positive flow accumulator integer part (REG 0009-0010)
            pos_flow_acc_int = self.device.read_register(
                start_address=0x0009, 
                register_count=2,
                data_format='>l'  # 32-bit long integer
            )
            
            # Read positive flow accumulator fraction part (REG 0011-0012)
            pos_flow_acc_frac = self.device.read_register(
                start_address=0x0011,
                register_count=2,
                data_format='>f'  # 32-bit float
            )
            
            # Read flow decimal point (REG 1439)
            flow_decimal_point = self.device.read_register(
                start_address=0x1439,
                register_count=1
            )
            
            # Read flow unit (REG 1438)
            flow_unit = self.device.read_register(
                start_address=0x1438,
                register_count=1
            )
            
            # Calculate actual flow accumulator value according to formula (N+Nf)×10^(n-3)
            if all(v is not None for v in [pos_flow_acc_int, pos_flow_acc_frac, flow_decimal_point]):
                pos_flow_acc = (pos_flow_acc_int + pos_flow_acc_frac) * (10 ** (flow_decimal_point - 3))
            else:
                pos_flow_acc = None
                
            # Read temperatures (°C) - IEEE754 format
            temp_supply = self.device.read_register(
                start_address=0x0033, 
                register_count=2,
                data_format='>f'
            )
            temp_return = self.device.read_register(
                start_address=0x0035, 
                register_count=2,
                data_format='>f'
            )
            
            # Check if any readings are None before rounding
            if any(v is None for v in [flow_rate, energy_flow, velocity, pos_flow_acc, temp_supply, temp_return]):
                print("Warning: One or more sensor readings returned None")
                return None
            
            # Map flow unit
            flow_unit_map = {
                0: "m3",
                1: "L",
                2: "GAL",
                3: "CF"
            }
            current_flow_unit = flow_unit_map.get(flow_unit, "m3")
            
            return {
                'flow_rate': round(flow_rate, 3),  # m3/h
                'energy_flow': round(energy_flow, 3),  # kW
                'velocity': round(velocity, 3),  # m/s
                'pos_flow_acc': round(pos_flow_acc, 3),  # Based on flow_unit
                'pos_flow_acc_unit': current_flow_unit,
                'temp_supply': round(temp_supply, 2),  # °C
                'temp_return': round(temp_return, 2)  # °C
            }
            
        except Exception as e:
            print(f"Error reading flow sensor: {e}")
            return None