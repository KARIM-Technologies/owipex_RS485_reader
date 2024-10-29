import struct
import serial
import crcmod.predefined
from threading import Thread, Lock
import time

class ModbusClient:
    def __init__(self, device_manager, device_id):
        self.device_manager = device_manager
        self.device_id = device_id

    def read_register(self, start_address, register_count, data_format='>f'):
        return self.device_manager.read_register(self.device_id, start_address, register_count, data_format)

    def read_radar_sensor(self, register_address):
        return self.device_manager.read_radar_sensor(self.device_id, register_address)

class DeviceManager:
    def __init__(self, port, baudrate, parity, stopbits, bytesize, timeout):
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            parity=serial.PARITY_NONE if parity == 'N' else serial.PARITY_EVEN if parity == 'E' else serial.PARITY_ODD,
            stopbits=serial.STOPBITS_ONE if stopbits == 1 else serial.STOPBITS_TWO,
            bytesize=serial.EIGHTBITS if bytesize == 8 else serial.SEVENBITS,
            timeout=timeout
        )
        self.devices = {}
        self.last_read_values = {}
        self._lock = Lock()

    def add_device(self, device_id):
        self.devices[device_id] = ModbusClient(self, device_id)
        return self.devices[device_id]

    def get_device(self, device_id):
        return self.devices.get(device_id)

    def _send_and_receive(self, message, expected_length):
        with self._lock:
            self.ser.reset_input_buffer()
            self.ser.write(message)
            time.sleep(0.1)  # Give device time to respond
            response = self.ser.read(expected_length)
            return response

    def read_register(self, device_id, start_address, register_count, data_format):
        function_code = 0x03
        message = struct.pack('>B B H H', device_id, function_code, start_address, register_count)
        crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')(message)
        message += struct.pack('<H', crc16)

        # Expected response length: 1 byte address + 1 byte function code + 1 byte length + 4 bytes data + 2 bytes CRC
        expected_length = 9
        response = self._send_and_receive(message, expected_length)

        if len(response) < expected_length:
            return self.last_read_values.get((device_id, start_address), None)

        received_crc = struct.unpack('<H', response[-2:])[0]
        calculated_crc = crcmod.predefined.mkPredefinedCrcFun('modbus')(response[:-2])
        
        if received_crc != calculated_crc:
            return self.last_read_values.get((device_id, start_address), None)

        data = response[3:-2]
        swapped_data = data[2:4] + data[0:2]
        
        try:
            value = struct.unpack(data_format, swapped_data)[0]
            self.last_read_values[(device_id, start_address)] = value
            return value
        except struct.error:
            return self.last_read_values.get((device_id, start_address), None)

    def read_radar_sensor(self, device_id, register_address):
        """Special method for reading radar sensor data with unsigned short format"""
        function_code = 0x03
        message = struct.pack('>B B H H', device_id, function_code, register_address, 1)
        crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')(message)
        message += struct.pack('<H', crc16)

        # Expected response length for radar sensor: 1 byte address + 1 byte function code + 1 byte length + 2 bytes data + 2 bytes CRC
        expected_length = 7
        response = self._send_and_receive(message, expected_length)

        if len(response) < expected_length:
            return self.last_read_values.get((device_id, register_address), None)

        received_crc = struct.unpack('<H', response[-2:])[0]
        calculated_crc = crcmod.predefined.mkPredefinedCrcFun('modbus')(response[:-2])
        
        if received_crc != calculated_crc:
            return self.last_read_values.get((device_id, register_address), None)

        data = response[3:-2]
        try:
            value = struct.unpack('>H', data)[0]
            self.last_read_values[(device_id, register_address)] = value
            return value
        except struct.error:
            return self.last_read_values.get((device_id, register_address), None)