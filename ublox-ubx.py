import serial
import time
import string

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
  
# CFG-RATE

# measRate=0xE800, navRate=0x0103
#msg_cfg_rate = b'\x06\x08\x06\x00\xE8\x03\x01\x00\x01\x00'

# measRate=0xE800, navRate=0x010F
msg_cfg_rate = b'\x06\x08\x06\x00\xE8\x0F\x01\x00\x01\x00'

# measRate=0x6400, navRate=0x0100
#msg_cfg_rate = b'\x06\x08\x06\x00\x64\x00\x01\x00\x01\x00'

hex_string = ''.join(['{:02x} '.format(byte) for byte in msg_cfg_rate])
print("Команда CFG-RATE без контрольной суммы: " + hex_string)

msg_to_write = b'\xB5\x62'
msg_to_write += msg_cfg_rate

checksum_a, checksum_b = calculate_checksum(msg_cfg_rate)
msg_to_write += bytes([checksum_a, checksum_b])

hex_string = ''.join(['{:02x} '.format(byte) for byte in msg_cfg_rate])
hex_string = ''.join(['{:02x} '.format(byte) for byte in msg_to_write])
print("Полная команда CFG-RATE: " +hex_string)

rc = isvalid_checksum(msg_to_write)
print("Контрольная сумма верна: " + str(rc))

port="/dev/ttyS0"
ser=serial.Serial(port, baudrate=9600, timeout=0.5)
rc = ser.write(msg_to_write)
print("Записано байт в UART: " + str(rc))
ser.close()

