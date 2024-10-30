from .sensor_base import SensorBase
import struct

class FlowSensor(SensorBase):
    def __init__(self, device_id, device_manager):
        super().__init__(device_id, device_manager)
        
    def _decode_ieee754(self, registers):
        """Decode two registers as IEEE 754 floating point"""
        try:
            # Convert registers to bytes and unpack as float
            bytes_data = struct.pack('>HH', registers[0], registers[1])
            value = struct.unpack('>f', bytes_data)[0]
            return value
        except Exception as e:
            print(f"Error decoding IEEE 754: {e}")
            return None
        
    def read_data(self):
        """Read flow sensor data with proper scaling"""
        try:
            # Read flow rate (m3/h) - IEEE 754
            flow_raw = self.device.read_register(start_address=0x0001, register_count=2, data_format='>HH')
            flow_rate = self._decode_ieee754(flow_raw)
            
            # Read energy flow (kW) - IEEE 754
            energy_raw = self.device.read_register(start_address=0x0003, register_count=2, data_format='>HH')
            energy_flow = self._decode_ieee754(energy_raw)
            
            # Read velocity (m/s) - IEEE 754
            velocity_raw = self.device.read_register(start_address=0x0005, register_count=2, data_format='>HH')
            velocity = self._decode_ieee754(velocity_raw)
            
            # Read net flow (m3) - IEEE 754
            net_flow_raw = self.device.read_register(start_address=0x0025, register_count=2, data_format='>HH')
            net_flow = self._decode_ieee754(net_flow_raw)
            
            # Read temperatures (°C) - IEEE 754
            temp1_raw = self.device.read_register(start_address=0x0033, register_count=2, data_format='>HH')  # T1 (Device)
            temp2_raw = self.device.read_register(start_address=0x0035, register_count=2, data_format='>HH')  # T2 (Flow)
            
            temp1 = self._decode_ieee754(temp1_raw)
            temp2 = self._decode_ieee754(temp2_raw)
            
            return {
                'flow_rate': round(flow_rate, 3) if flow_rate is not None else None,  # m3/h
                'energy_flow': round(energy_flow, 3) if energy_flow is not None else None,  # kW
                'velocity': round(velocity, 3) if velocity is not None else None,  # m/s
                'net_flow': round(net_flow, 3) if net_flow is not None else None,  # m3
                'temp_device': round(temp1, 2) if temp1 is not None else None,  # °C (T1)
                'temp_flow': round(temp2, 2) if temp2 is not None else None,  # °C (T2)
            }
            
        except Exception as e:
            print(f"Error reading flow sensor: {e}")
            return None