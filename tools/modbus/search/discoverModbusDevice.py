import struct
import serial
import crcmod.predefined

class ModbusClient:
    def __init__(self, port, baudrate, parity, stopbits, bytesize, timeout):
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            parity=serial.PARITY_NONE if parity == 'N' else serial.PARITY_EVEN if parity == 'E' else serial.PARITY_ODD,
            stopbits=serial.STOPBITS_ONE if stopbits == 1 else serial.STOPBITS_TWO,
            bytesize=serial.EIGHTBITS if bytesize == 8 else serial.SEVENBITS,
            timeout=timeout
        )

    def read_register(self, device_id, start_address, register_count):
        function_code = 0x03  # Function code for Read Holding Registers
        message = struct.pack('>B B H H', device_id, function_code, start_address, register_count)
        crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')(message)
        message += struct.pack('<H', crc16)
        self.ser.write(message)
        response = self.ser.read(5 + 2 * register_count)
        return struct.unpack('>H', response[3:5])[0]  # Return the value from the first register in the response

    def discover_devices(self, start_id=1, end_id=247):
        devices = []
        for device_id in range(start_id, end_id+1):
            print(f"Testing device ID: {device_id}")  # Ausgabe des aktuellen Geräte-IDs
            try:
                self.read_register(device_id, 0, 1)  # versucht ein Register von jedem Gerät zu lesen
                devices.append(device_id)  # wenn erfolgreich, füge die Geräte-ID der Liste hinzu
                print(f"Found device at ID: {device_id}")  # Ausgabe der gefundenen Geräte-IDs
            except:
                print(f"No device at ID: {device_id}")  # Ausgabe, wenn kein Gerät gefunden wurde
        return devices

# Erstellen Sie ein ModbusClient-Objekt mit Ihren spezifischen Port- und Verbindungseinstellungen
client = ModbusClient(port='/dev/ttyS0', baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=1)

# Finden Sie alle Geräte und drucken Sie ihre IDs aus
devices = client.discover_devices()
print(f'Found devices: {devices}')