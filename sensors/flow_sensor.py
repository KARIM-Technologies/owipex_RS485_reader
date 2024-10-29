from .sensor_base import SensorBase

class FlowSensor(SensorBase):
    def __init__(self, device_id, device_manager):
        super().__init__(device_id, device_manager)
        
    def read_data(self):
        """Read flow sensor data"""
        try:
            flow_rate = self.device.read_register(start_address=0x0001, register_count=2)  # m3/h
            energy_flow = self.device.read_register(start_address=0x0003, register_count=2)  # kW
            velocity = self.device.read_register(start_address=0x0005, register_count=2)  # m/s
            net_flow = self.device.read_register(start_address=0x0025, register_count=2)  # m3
            temp_supply = self.device.read_register(start_address=0x0033, register_count=2)  # °C
            temp_return = self.device.read_register(start_address=0x0035, register_count=2)  # °C
            
            return {
                'flow_rate': flow_rate,
                'energy_flow': energy_flow,
                'velocity': velocity,
                'net_flow': net_flow,
                'temp_supply': temp_supply,
                'temp_return': temp_return
            }
        except Exception as e:
            print(f"Error reading flow sensor: {e}")
            return None