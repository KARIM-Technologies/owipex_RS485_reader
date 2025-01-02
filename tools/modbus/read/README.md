# ModbusSensorRS485

# Modbus Lib
KARIM Technologies, Sayed Amir Karim, Copyright 2023 KARIM Technologies

## Overview
The Modbus Lib by KARIM Technologies is a Python library for communicating with devices over Modbus RTU protocol. It supports reading registers from devices connected to a serial port. The library is easy to use and fully compatible with Python 3.

## Features
- Modbus RTU protocol support
- Reading of device registers
- Automatic continuous reading of registers at specified intervals
- Handling multiple devices connected to the same port

## Installation
To install the library, you can clone this repository to your local machine. 

```bash
git clone https://github.com/KARIMTechnologies/modbus_lib.git

Then, navigate to the cloned repository and install the required dependencies.

cd modbus_lib
pip install -r requirements.txt


Usage
To use the library, you create a DeviceManager with the appropriate settings for your serial port. Then, you can add devices and read their registers.

from modbus_lib import DeviceManager

dev_manager = DeviceManager(port='/dev/ttymxc3', baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=1)
dev_manager.add_device(device_id=0x01)
sensor1 = dev_manager.get_device(device_id=0x01)
temperature = sensor1.read_register(start_address=0x0003, register_count=2)



## Sonden
- RMD-ISHP105 PH Sonde
    blau    = 0V
    braun   = 12V 
    weiss   = A
    schwarz = B