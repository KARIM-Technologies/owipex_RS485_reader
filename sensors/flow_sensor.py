from .sensor_base import SensorBase

class FlowSensor(SensorBase):
    def __init__(self, device_id, device_manager):
        super().__init__(device_id, device_manager)
        
    def read_data(self):
        """Read flow sensor data with proper IEEE754 formatting"""
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
            
            # Read positive flow accumulator (m3) - LONG format
            pos_flow_acc = self.device.read_register(
                start_address=0x0009, 
                register_count=2,
                data_format='>l'  # 32-bit long integer
            )
            
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
            
            return {
                'flow_rate': round(flow_rate, 3),  # m3/h
                'energy_flow': round(energy_flow, 3),  # kW
                'velocity': round(velocity, 3),  # m/s
                'pos_flow_acc': pos_flow_acc,  # m3 (accumulated)
                'temp_supply': round(temp_supply, 2),  # °C
                'temp_return': round(temp_return, 2)  # °C
            }
            
        except Exception as e:
            print(f"Error reading flow sensor: {e}")
            return None