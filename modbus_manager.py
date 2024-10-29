import struct
import serial
import crcmod.predefined
from threading import Thread
from time import sleep

class ModbusClient:
    def __init__(self, device_manager, device_id):
        self.device_manager = device_manager
        self.device_id = device_id

    def read_register(self, start_address, register_count, data_format='>f'):
        return self.device_manager.read_register(self.device_id, start_address, register_count, data_format)

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

    def add_device(self, device_id):
        self.devices[device_id] = ModbusClient(self, device_id)
        return self.devices[device_id]

    def get_device(self, device_id):
        return self.devices.get(device_id)

    def read_register(self, device_id, start_address, register_count, data_format):
        function_code = 0x03
        message = struct.pack('>B B H H', device_id, function_code, start_address, register_count)
        crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')(message)
        message += struct.pack('<H', crc16)

        self.ser.write(message)
        response = self.ser.read(100)

        if len(response) < 2:
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