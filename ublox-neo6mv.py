import serial
import time
import string
import pynmea2

# https://github.com/semuconsulting/pyubx2/blob/master/src/pyubx2/ubxhelpers.py

def calculate_checksum(content: bytes) -> bytes:
    """
    Calculate checksum using 8-bit Fletcher's algorithm.

    :param bytes content: message content, excluding header and checksum bytes
    :return: checksum
    :rtype: bytes

    """

    check_a = 0
    check_b = 0

    for char in content:
        check_a += char
        check_a &= 0xFF
        check_b += check_a
        check_b &= 0xFF

    return bytes((check_a, check_b))

def isvalid_checksum(message: bytes) -> bool:
    """
    Validate message checksum.

    :param bytes message: message including header and checksum bytes
    :return: checksum valid flag
    :rtype: bool

    """

    lenm = len(message)
    ckm = message[lenm - 2 : lenm]
    return ckm == calculate_checksum(message[2 : lenm - 2])
  

#msg = b'\xB5\x62\x06\x08\x06\x00\x64\x00\x01\x00\x01\x00\x7A\x12'
#msg = b'\xB5\x62\x06\x08\x06\x00\xE8\x03\x01\x00\x01\x00\xF0\xAE'

#msg_test = b'\x06\x08\x06\x00\x64\x00\x01\x00\x01\x00'
#msg_test = b'\x06\x08\x06\x00\xE8\x03\x01\x00\x01\x00'
msg_test = b'\x06\x08\x06\x00\xE8\x0F\x01\x00\x01\x00'


hex_string = ''.join(['{:02x} '.format(byte) for byte in msg_test])
print(hex_string)

msg_test2 = b'\xB5\x62'
msg_test2 += msg_test

checksum_a, checksum_b = calculate_checksum(msg_test)
msg_test2 += bytes([checksum_a, checksum_b])

hex_string = ''.join(['{:02x} '.format(byte) for byte in msg_test])
print(hex_string)

hex_string = ''.join(['{:02x} '.format(byte) for byte in msg_test2])
print(hex_string)

rc = isvalid_checksum(msg_test2)
print(rc)

port="/dev/ttyS2"
ser=serial.Serial(port, baudrate=9600, timeout=0.5)

# Отправляем сообщение
rc = ser.write(msg_test2)

# Закрываем порт
ser.close()
print(rc)

