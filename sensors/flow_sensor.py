from .sensor_base import SensorBase

class FlowSensor(SensorBase):
    def __init__(self, device_id, device_manager):
        super().__init__(device_id, device_manager)
        
    def read_data(self):
        """Read flow sensor data with proper scaling"""
        try:
            # Read flow rate (m3/h) - 32-bit float
            flow_rate = self.device.read_register(start_address=0x0001, register_count=2)
            
            # Read energy flow (kW) - 32-bit float  
            energy_flow = self.device.read_register(start_address=0x0003, register_count=2)
            
            # Read velocity (m/s) - 32-bit float
            velocity = self.device.read_register(start_address=0x0005, register_count=2)
            
            # Read net flow (m3) - 32-bit float
            net_flow = self.device.read_register(start_address=0x0025, register_count=2)
            
            # Read temperatures (°C) - 32-bit float
            temp_supply = self.device.read_register(start_address=0x0033, register_count=2)
            temp_return = self.device.read_register(start_address=0x0035, register_count=2)
            
            return {
                'flow_rate': round(flow_rate, 3),  # m3/h
                'energy_flow': round(energy_flow, 3), # kW
                'velocity': round(velocity, 3), # m/s
                'net_flow': round(net_flow, 3), # m3
                'temp_supply': round(temp_supply, 2), # °C
                'temp_return': round(temp_return, 2) # °C
            }
            
        except Exception as e:
            print(f"Error reading flow sensor: {e}")
            return None