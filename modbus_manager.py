import struct
import serial
import crcmod.predefined
from threading import Thread, Lock
import time
import logging

# Logger für ModbusManager
logger = logging.getLogger('ModbusManager')

class ModbusClient:
    def __init__(self, device_manager, device_id):
        self.device_manager = device_manager
        self.device_id = device_id

    def read_register(self, start_address, register_count=1, data_format='>H'):
        return self.device_manager.read_register(self.device_id, start_address, register_count, data_format)

    def read_radar_sensor(self, register_address):
        return self.device_manager.read_radar_sensor(self.device_id, register_address)
        
    def read_flow_sensor(self, register_address):
        return self.device_manager.read_flow_sensor(self.device_id, register_address)

    def write_registers(self, start_address, values):
        return self.device_manager.write_registers(self.device_id, start_address, values)

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

    def remove_device(self, device_id):
        """Entfernt ein Gerät aus dem DeviceManager"""
        if device_id in self.devices:
            del self.devices[device_id]
            # Entferne auch alle gespeicherten Werte für dieses Gerät
            self.last_read_values = {k: v for k, v in self.last_read_values.items() if k[0] != device_id}
            return True
        return False

    def get_device(self, device_id):
        return self.devices.get(device_id)

    def _send_and_receive(self, message, expected_length):
        with self._lock:
            self.ser.reset_input_buffer()
            self.ser.write(message)
            time.sleep(0.1)  # Give device time to respond
            response = self.ser.read(expected_length)
            return response

    def read_register(self, device_id, start_address, register_count=1, data_format='>H'):
        logger = logging.getLogger('ModbusManager')
        try:
            function_code = 0x03
            message = struct.pack('>B B H H', device_id, function_code, start_address, register_count)
            crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')(message)
            message += struct.pack('<H', crc16)

            # Gib der Antwort mehr Zeit
            self.ser.reset_input_buffer()
            self.ser.write(message)
            time.sleep(0.2)  # Erhöhe die Wartezeit auf 200ms

            # Lese zuerst den Header (3 Bytes)
            header = self.ser.read(3)
            if len(header) != 3:
                logger.error(f"Keine oder unvollständige Header-Antwort von Gerät {device_id}")
                return None

            # Extrahiere die Datenlänge aus dem Header
            byte_count = header[2]
            
            # Lese den Rest der Nachricht (Daten + 2 Bytes CRC)
            remaining = self.ser.read(byte_count + 2)
            if len(remaining) != (byte_count + 2):
                logger.error(f"Unvollständige Daten von Gerät {device_id}")
                return None

            response = header + remaining
            
            # CRC Prüfung
            received_crc = struct.unpack('<H', response[-2:])[0]
            calculated_crc = crcmod.predefined.mkPredefinedCrcFun('modbus')(response[:-2])
            
            if received_crc != calculated_crc:
                logger.error(f"CRC-Fehler bei Gerät {device_id}, Register {hex(start_address)}")
                return None

            data = response[3:-2]
            try:
                if register_count == 2:
                    # Für 32-bit Float-Werte
                    if len(data) != 4:
                        logger.error(f"Falsche Datenlänge für Float-Wert: {len(data)} Bytes")
                        return None
                    swapped_data = data[2:4] + data[0:2]
                    value = struct.unpack('>f', swapped_data)[0]
                else:
                    # Für 16-bit Werte
                    if len(data) != 2:
                        logger.error(f"Falsche Datenlänge für Integer-Wert: {len(data)} Bytes")
                        return None
                    value = struct.unpack('>H', data)[0]

                self.last_read_values[(device_id, start_address)] = value
                logger.debug(f"Erfolgreich gelesen von Gerät {device_id}, Register {hex(start_address)}: {value}")
                return value
            except struct.error as e:
                logger.error(f"Fehler beim Entpacken der Daten von Gerät {device_id}, Register {hex(start_address)}: {e}")
                return None
        except Exception as e:
            logger.error(f"Allgemeiner Fehler beim Lesen von Gerät {device_id}, Register {hex(start_address)}: {e}")
            return None

    def read_radar_sensor(self, device_id, register_address):
        """Special method for reading radar sensor data with unsigned short format"""
        function_code = 0x03
        message = struct.pack('>B B H H', device_id, function_code, register_address, 1)
        crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')(message)
        message += struct.pack('<H', crc16)

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

    def read_flow_sensor(self, device_id, register_address):
        """Special method for reading flow sensor data with 32-bit float format"""
        with self._lock:
            try:
                # Einfache Version wie im Port-Tester
                function_code = 0x03
                message = struct.pack('>BBHH', device_id, function_code, register_address, 2)
                message += struct.pack('<H', crcmod.predefined.mkPredefinedCrcFun('modbus')(message))

                # Clear buffers
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
                
                # Send request
                self.ser.write(message)
                self.ser.flush()
                
                # Fixed wait time
                time.sleep(0.1)
                
                # Read response
                response = self.ser.read(9)  # Erwarte genau 9 Bytes
                
                if len(response) == 9:
                    # CRC check
                    received_crc = struct.unpack('<H', response[-2:])[0]
                    calculated_crc = crcmod.predefined.mkPredefinedCrcFun('modbus')(response[:-2])
                    
                    if received_crc == calculated_crc:
                        data = response[3:-2]
                        value = struct.unpack('>f', data)[0]
                        self.last_read_values[(device_id, register_address)] = value
                        return value
                
                return self.last_read_values.get((device_id, register_address), None)
                    
            except Exception as e:
                logger.error(f"Fehler beim Lesen von Flow Sensor {device_id}: {e}")
                return self.last_read_values.get((device_id, register_address), None)

    def write_registers(self, device_id, start_address, values):
        """Write multiple registers using Modbus function code 0x10"""
        function_code = 0x10
        register_count = len(values)
        byte_count = register_count * 2
        
        # Erstelle die Nachricht: device_id + function_code + start_address + register_count + byte_count + values
        message = struct.pack('>B B H H B', device_id, function_code, start_address, register_count, byte_count)
        
        # Füge die Werte hinzu
        for value in values:
            message += struct.pack('>H', value)
            
        # Berechne und füge CRC hinzu
        crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')(message)
        message += struct.pack('<H', crc16)

        # Erwartete Antwortlänge für Funktion 0x10 ist 8 Bytes
        expected_length = 8
        response = self._send_and_receive(message, expected_length)

        if len(response) < expected_length:
            raise Exception("Keine oder unvollständige Antwort vom Gerät")

        # Überprüfe die Antwort
        received_crc = struct.unpack('<H', response[-2:])[0]
        calculated_crc = crcmod.predefined.mkPredefinedCrcFun('modbus')(response[:-2])
        
        if received_crc != calculated_crc:
            raise Exception("CRC-Prüfung fehlgeschlagen")

        # Überprüfe die Antwort auf Fehler
        if response[1] != function_code:
            raise Exception(f"Unerwarteter Funktionscode in der Antwort: {response[1]}")

        return True