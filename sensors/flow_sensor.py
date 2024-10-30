from .sensor_base import SensorBase

class FlowSensor(SensorBase):
    def __init__(self, device_id, device_manager):
        super().__init__(device_id, device_manager)
        
    def read_data(self):
        """Read flow sensor data"""
        try:
            # Use specialized flow sensor reading method for better accuracy
            flow_rate = self.device.read_flow_sensor(0x0001)  # m3/h
            energy_flow = self.device.read_flow_sensor(0x0003)  # kW
            velocity = self.device.read_flow_sensor(0x0005)  # m/s
            net_flow = self.device.read_flow_sensor(0x0025)  # m3
            temp_supply = self.device.read_flow_sensor(0x0033)  # °C
            temp_return = self.device.read_flow_sensor(0x0035)  # °C
            
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