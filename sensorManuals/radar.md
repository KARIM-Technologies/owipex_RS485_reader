8.Communication protocol command description
Each command is described in detail as follows: Setting command: function code 0x10
Read command: function code 0x03
Start address 0x2000
Note: Each parameter occupies a register address, and the data is in U16 or I16 format give an example:
Read the low order adjustment command as follows:
Write the low order adjustment command as follows:
CRC code calculation rules:
16 bit registers are reserved as hexadecimal FFFF (that is, all are 1).This register bit CRC odd memory; Put the position of the first 8-bit data and the 16 bit CRC register in different positions or place the result in the CRC register:
Check whether the lowest bit is 0, if so.Move the contents of the register one bit to the right (towards the low bit), and fill the high bit with;
If it is 1, move the contents of the register to the right by one bit (toward the low bit), fill the high bit with, and then CRC odd memory and polynomial A001
(1010 0000 0000 0001);4.3.4 Repeat step 3 until 8 times to the right, so that the entire 8-bit data is processed: repeat steps 2 to 4 to process the next 8-bit data;The final CRC odd memory is CRC code.When CRC results are put into the information frame, the high bit is exchanged, and the low bit is first.
Communication protocol example:
Host sends data:
Offset address
Command name
data format
Company
0
Low adjustment
0-65000
mm
1
High level adjustment
0-65000
mm
2
range
0-65000
mm
Device address
Function code
Start address
Number of registers
CRC
0x01
0x03
0x2000
(2 bytes)
(2 bytes)
Device address
Function code
Start address
Number of registers
Data length
Register value
CRC
0x01
0x10
0x2000
2 bytes
(2 bytes)
(2N bytes)
(2 bytes)
 
 
Station No
Function code
Start address
Reading points
Check code
significance
01
03
0000
0001
840A
Read the empty height in cm
01
03
0001
0001
D5CA
Read the empty height in mm
01
03
0002
0001
25CA
Read the liquid level in cm
01
03
0003
0001
740A
Read the liquid level in mm