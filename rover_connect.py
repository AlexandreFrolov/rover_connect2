import traceback
import pdb
import re
import time
import datetime
import json
from collections import namedtuple
from sim800l import SIM800L


class SmsTz(datetime.tzinfo):
    hours = 0
    def __init__(self, h):
        self.hours = h
    def utcoffset(self, dt):
         return datetime.timedelta(hours=self.hours)
    def dst(self, dt):
        return datetime.timedelta(0)

class RoverConnect(SIM800L):
    def __init__(self, serial_port, apn='internet.mts.ru'):
        super().__init__(serial_port, timeout=15.0)        
        self.setup()
        self.debug = 0
        self.apn=apn

    def power_supported_modes(self):
        pwr_supported_modes = self.command_data_ok('AT+CGNSPWR=?')
        matches = re.findall(r'\((.*?)\)', pwr_supported_modes)
        return matches[0]
        
    def power_current_status(self):
        power_status = self.command_data_ok('AT+CGNSPWR?')
        matches = re.findall(r'\+CGNSPWR: (\d+)', power_status)
        return matches[0]       
    
    def creg_status(self):
        creg_data = self.command_data_ok('AT+CREG?')
        value_0 = None
        value_1 = None
        
        if creg_data.startswith("+CREG: "):
            creg_params = creg_data.split(':')[1].strip()
            split_result = creg_params.split(',')
            value_0 = split_result[0].strip()
            value_1 = split_result[1].strip()
            
        return value_0, value_1
        
    def cpin_status(self):
        cpin = self.command_data_ok('AT+CPIN?')
        status = None
        if cpin.startswith("+CPIN: "):
            pin = cpin.split(':')[1].strip()
        return pin        

    def cgnsurc_supported_modes(self):
        urc_supported_modes = self.command_data_ok('AT+CGNSURC=?')
        matches = re.findall(r'\((.*?)\)', urc_supported_modes)
        return matches[0]    

    def cgnsurc_settings(self):
        settings = self.command_data_ok('AT+CGNSURC?')
        matches = re.findall(r'\+CGNSURC: (\d+)', settings)
        return matches[0]

    def get_cgns_data(self):
        gnss_data = self.command_data_ok('AT+CGNSINF')
        gnss_data = gnss_data.replace("+CGNSINF: ", "")
        return gnss_data
        
    def parse_cgns_info(self, data_string):
        CGNSInfo = namedtuple("CGNSInfo", [
            "gnss_status", "fix_status", "utc_datetime",
            "latitude", "longitude", "msl_altitude",
            "speed", "course", "fix_mode", "reserved_1",
            "hdop", "pdop", "vdop", "reserved_2", "satellites_in_view",
            "gnss_satellites_used", "glonass_satellites_used",
            "reserved_3", "c_n0_max", "hpa", "vpa"
        ])
        
        substring_to_remove = 'AT+CGNSINF\r\r\n+CGNSINF: '
        substring_to_remove_from_end = '\r\n\r\nOK'
        data_string = data_string.replace(substring_to_remove, '')
        data_string = data_string.replace(substring_to_remove_from_end, '')
        parts = data_string.strip().split(",")
        
        cgns_info = CGNSInfo(
            gnss_status=parts[0], fix_status=parts[1], utc_datetime=parts[2],
            latitude=parts[3], longitude=parts[4], msl_altitude=parts[5],
            speed=parts[6], course=parts[7], fix_mode=parts[8],
            reserved_1=parts[9], hdop=parts[10], pdop=parts[11],
            vdop=parts[12], reserved_2=parts[13],
            satellites_in_view=parts[14],
            gnss_satellites_used=parts[15], glonass_satellites_used=parts[16],
            reserved_3=parts[17], c_n0_max=parts[18], hpa=parts[19], vpa=parts[20]
        )
        if cgns_info.gnss_status != '1' or cgns_info.fix_status != '1':
            raise Exception(f"failed with error: GNSS Position not fixed")
            
            
        cgns_info_dict = cgns_info._asdict()

        # Преобразуйте словарь в JSON-строку
        telemetry_json = json.dumps(cgns_info_dict, ensure_ascii=False, indent=2)            
            
        return telemetry_json
        
    def generate_google_maps_link(self, latitude, longitude):
        return f"https://www.google.com/maps/place/{latitude},{longitude}"

    def generate_openstreetmap_link(self, latitude, longitude):
        return f"https://www.openstreetmap.org/?mlat={latitude}&mlon={longitude}"

    def generate_yandex_maps_link(self, latitude, longitude):
        return f"https://yandex.ru/maps/?pt={longitude},{latitude}&z=18&l=map"    

    def getMtsBalance(self):
        self.command("AT+CUSD=1,\"#100#\",15\n", lines=0)
        expire = time.monotonic() + 5  # seconds
        sequence = ""
        s = self.check_incoming()
        balance = None
        while time.monotonic() < expire:
            if s[0] == 'GENERIC' and s[1]:
                if '+CUSD:' in s[1]:
                    parts = s[1].split(', ')
                    balance = parts[1].replace('Balance:', '').strip(' "r')
                    sequence += "O"
            if s == ('OK', None):
                sequence += "D"
            if sequence == "DO":
                break
            time.sleep(0.1)
            s = self.check_incoming()
        if sequence != "DO":
            return(None)
        return(balance)


    # Преобразование строки символов в формат SMS
    #
    # Каждый двухбайтовый юникодный символ в строке разбивается на пару байт,
    # и формируется новая строка, состоящая из шестнадцатеричных представлений этих байтов
    #
    # Возвращаемое значение - строка, содержащая строку символов в формате SMS
    #
    def text_to_sms(self, text):
        b = text
        result = ''
        i = 0
        while i < len(b):
            o = ord(b[i])
    #        result += ("%0.2X" % (o/256)) + ("%0.2X" % (o%256))
            result += ("%0.2X" % (o // 256)) + ("%0.2X" % (o % 256))
            i += 1
        return result

    # Преобразование номера телефона в международном формате в формат SMS
    #
    # Исходная строка, содержащая телефон в международном формате 79130123456,
    # дополняется справа символом F                                                            - 79130123456F,
    # разбивается на пары символов                                                             - 79 13 01 23 45 6F,
    # в каждой паре символы меняются местами                                                   - 97 31 10 32 54 F6,
    # слева приписывается идентификатор международного формата (91)                            - 91 97 31 10 32 54 F6,
    # слева приписывается количество цифр в телефоне, т.е. 11 в шестнадцатеричном формате (0B) - 0B 91 97 31 10 32 54 F6
    #
    # Возвращаемое значение - строка, содержащая закодированный номер телефона 0B919731103254F6
    #
    def phone_number_to_sms(self, number):
        number += 'F'
        result = '0B' + '91'
        i = 0
        while i < len(number):
            result += number[i+1] + number[i]
            i += 2
        return result


    # Восстановление номера телефона в международном формате в из формата SMS
    #
    # Исходная строка, содержащая закодированный телефон 9731103254F6
    # разбивается на пары символов           - 97 31 10 32 54 F6,
    # в каждой паре символы меняются местами - 79 13 01 23 46 6F,
    # убирается символ F                     - 79130123456
    #
    # Возвращаемое значение - строка, содержащая номер телефона 79130123456
    #
    def sms_to_phone_number(self, data):
        result = ""
        i = 0
        while i < len(data):
            result += data[i+1] + data[i]
            i += 2
        return result[:-1]


    # Восстановление даты и времени из их представления SMS
    #
    # На вход подается закодированная строка  - 11113131516461
    # эта строка разбивается на пары символов - 11 11 31 31 51 64 61,
    # в каждой паре символы меняются местами  - 11 11 13 13 15 46 16,
    # получившиеся строки трактуются как шестнадцатиричные представления байтов - 0x11 0x11 0x13 0x13 0x15 0x46 0x16
    # эти байты представляют собой соответственно год, месяц, день, часы, минуты, секунды, часовой пояс
    # часовой пояс представляется как количество четвертей часа, т.е. 0x16 = GMT+4 (седьмой бит отвечает за знак)
    #
    # Возвращаемое значение - дата и время 2011-11-13 13:15:46+04:00
    #
    def sms_to_time_stamp(self, text):
        year   = int(text[1] + text[0]) + 2000
        month  = int(text[3] + text[2])
        day    = int(text[5] + text[4])
        hour   = int(text[7] + text[6])
        minute = int(text[9] + text[8])
        second = int(text[11] + text[10])
        tz     = int(text[13] + text[12])
        tz = ( (tz & 0x7F) if (tz & 0x80 == 0) else -(tz & 0x7F) ) / 4
        return datetime.datetime(year, month, day, hour, minute, second, 0, SmsTz(tz))


    # Восстановление строки из её семибитного кода
    #
    # На вход подается закодированная строка  - 4DEA10
    # эта строка разбивается на пары символов - 4D EA 10,
    # каждая пара трактуется как шестнадцатиричное представление байта - 0x4D 0xEA 0x10 = 01001101 11101010 00010000
    # из первого байта 01001101 берутся семь младших битов 1001101 и преобразуются в соответствующий символ ASCII - M
    # оставшийся бит 0 дополняется слева шестью младшими битами второго байта 101010: 1010100 - T
    # оставшиеся два бита 11 дополняются слева пятью младшими битами третьего байта 10000: 1000011 - С
    # и т.д.
    #
    # Возвращаемое значение - раскодированная строка MTC
    #
    def decode_7bit(self, text):
        result = ''

        bytes = [int(text[i*2:i*2+2], 16) for i in range(0, len(text) // 2)]
         
        symbol = 0
        bits   = 0
        n      = 0

        while n < len(bytes):

            if bits == 7:
                result += chr(symbol)
                symbol = 0
                bits   = 0
            else:
                symbol += (bytes[n] & (0x7F >> bits)) << bits
                result += chr(symbol)
                symbol = (bytes[n] & (0x7F << (7-bits))) >> (7-bits)
                bits   = (8-7) + bits
                n += 1

        if bits > 0 and symbol != 0:
            result += chr(symbol)

        return result


    # Восстановление строки символов в из формата SMS
    #
    # Исходная строка разбивается на четверки символов, которые преобразуются в целые числа
    # и формируется строка, состоящая из соответствующих этим числам символов
    #
    # Возвращаемое значение - раскодированная строка
    #
    def sms_to_text(self, text):
        result = u''
        i = 0
        while i+3 < len(text):
            result += chr(int(text[i] + text[i+1] + text[i+2] + text[i+3],16))
            i += 4
        return result


    # процедура для отправки строки в модем и получения ответа
    def str_send (self, textline):
#        if self.debug == 1:
#            print("<<" + textline)
        self.ser.write(bytes(textline, "utf-8"))
        out = ''
        N = 10
        while N > 0:
            time.sleep(1)
            while self.ser.inWaiting() > 0:
                out += str(self.ser.read(1))
            if ('OK' in out) or ('ERROR' in out) or ('>' in out):
#                if self.debug == 1:
#                    print(">>" + out)
                N = 1
            N -= 1
#        print(">>" + out)

    # Обмен с последовательным портом
    def str_send_bytes (self, textline):
        self.ser.write(textline.encode('utf-8'))

        out = b''
        # let's wait one second before reading output (let's give device time to answer)
        N = 10
        while N > 0:
            time.sleep(1)
            while self.ser.inWaiting() > 0:
                out += self.ser.read(1)

            if (b'OK' in out) or (b'ERROR' in out) or (b'>' in out):
                N = 1

            N -= 1

        return out.decode('utf-8')



    def send_sms(self, phone_number, message):
        # устанавливаем нужный формат передачи данных
        self.str_send('AT+CMGF=0\r')
    
        chunks = []

        if len(message) > 70:
            while len(message) > 66:
                chunks.append(message[:66])
                message = message[66:]
        if len(message) > 0:
            chunks.append(message)

        # готовим номер группы сообщений и устанавливаем 6-й бит SMS_SUBMIT_PDU
        SMS_SUBMIT_PDU = "11"
        CSMS_reference_number = ""
        if len(chunks) > 1:
            SMS_SUBMIT_PDU = "51"
            CSMS_reference_number = "%0.4X" % random.randrange(1,65536)

        # передаем кусочки сообщения
        i = 1
        for chunk in chunks:
            emessage = self.text_to_sms(chunk)
            if CSMS_reference_number != "":
                emessage = "06" + "08" + "04" + CSMS_reference_number + \
                ("%0.2X" % len(chunks)) + ("%0.2X" % i) + emessage
            sms = "00" #Накидываем тело сообщения в формате PDU
            sms += SMS_SUBMIT_PDU
            sms += "00"
            sms += self.phone_number_to_sms(phone_number)
            sms += "00"
            sms += "08"
            sms += "AA"
            sms += "%0.2X" % (len(emessage)//2)
            sms += emessage
            self.str_send('AT+CMGS=' + str(len(sms)//2-1) + '\r')
            self.str_send(sms + '\x1A')
            i += 1

        # отвязываемся от модема
        #self.ser.close()


    # отправка пин-кода в открытый порт
    def send_pin_to_port(self, pin):
        self.str_send_bytes('AT+CPIN="%s"\r' % (pin))

    # отправка пин-кода модему
    def send_pin(self, pin):
        # отправляем пин-код
        self.send_pin_to_port(pin)


    def delete_all_sms(self):
       # устанавливаем формат передачи сообщения - PDU
        self.command_ok('AT+CMGF=0')
        self.command_ok('AT+CMGDA=6')
        self.check_incoming()

    # удаление SMS сообщения в слоте с номером slot с сим-карты
    def delete_sms(self, slot, pin=None):
        # удаляем сообщение
        status = self.str_send_bytes('AT+CMGD=%s\r' % (slot))

        # если в ответ пришел текст, содержащий SIM PIN REQUIRED, значит, модему нужен пин-код
        if 'SIM PIN' in status:
            self.send_pin_to_port(ser, pin)
            self.str_send_bytes('AT+CMGD=%s\r' % (slot))


    # чтение SMS сообщений с сим-карты
    #
    # возвращаемое значение: список, состоящий из кортежей, каждый из которых содержит
    # номер слота на сим-карте, в котором находится сообщение (0-19),
    # номер телефона отправителя,
    # дату отправления сообщения,
    # текст сообщения
    #
    def get_sms(self, pin=None):
        result = []

        # устанавливаем формат передачи сообщения - PDU
        status = self.str_send_bytes('AT+CMGF=0\r')

        # если в ответ пришел текст, содержащий SIM PIN REQUIRED, значит, модему нужен пин-код
        if 'SIM PIN' in status:
            self.send_pin_to_port(pin)
            self.str_send_bytes('AT+CMGF=0\r')

        # запрашиваем список сообщений (4 - все сообщения)
        messages = self.str_send_bytes('AT+CMGL=4\r')

        if 'ERROR' not in messages:
            strings = messages.split('\n')
            i = 0

            while i < len(strings):
                if '+CMGL: ' in strings[i]:

                    message_header = strings[i][7:]
                    message_body = strings[i+1]
                    
                    offset = 0

                    SMSC_length = int(message_body[offset:offset+2],16)
                    offset += 2

                    SMSC_address = message_body[offset:offset+2*SMSC_length]
                    SMSC_typeOfAddress = SMSC_address[:2]
                    SMSC_serviceCenterNumber = self.sms_to_phone_number( SMSC_address[2:] )
                    offset += 2*SMSC_length

                    SMS_deliverBits = int(message_body[offset:offset+2],16)
                    offset += 2

                    SMS_senderNumberLength = int(message_body[offset:offset+2],16)
                    offset += 2

                    SMS_senderNumberType = message_body[offset:offset+2]
                    offset += 2

                    SMS_senderNumber = message_body[offset:offset+SMS_senderNumberLength+(1 if SMS_senderNumberLength & 1 != 0 else 0) ]
                    if SMS_senderNumberType == '91':
                        SMS_senderNumber = self.sms_to_phone_number(SMS_senderNumber)
                    if int(SMS_senderNumberType[0],16) & 5 == 5:
                        SMS_senderNumber = self.decode_7bit(SMS_senderNumber)
                    offset += SMS_senderNumberLength+(1 if SMS_senderNumberLength & 1 != 0 else 0)

                    TP_protocolIdentifier = message_body[offset:offset+2]
                    offset += 2

                    TP_dataCodingScheme = int(message_body[offset:offset+2],16)
                    offset += 2

                    TP_serviceCenterTimeStamp = self.sms_to_time_stamp(message_body[offset:offset+14])
                    offset += 14

                    TP_userDataLength = int(message_body[offset:offset+2],16)
                    offset += 2

                    if SMS_deliverBits & 64 != 0:
                        SMS_userDataHeaderLength = int(message_body[offset:offset+2],16)
                        offset += 2
                        SMS_userDataHeader = message_body[offset:offset+2*SMS_userDataHeaderLength]
                        offset += 2*SMS_userDataHeaderLength

                    message_text = None
                    if (TP_dataCodingScheme == 0):
                        message_text = self.decode_7bit(message_body[offset:])
                    if (TP_dataCodingScheme & 8 != 0):
                        message_text = self.sms_to_text(message_body[offset:])
                    if message_text is None:
                        message_text = message_body[offset:]

                    # добавляем в результирующий список кортеж, содержащий
                    # номер слота на сим-карте, в котором находится сообщение (0-19),
                    # номер телефона отправителя,
                    # дату отправления сообщения,
                    # текст сообщения
                    result.append((message_header.split(',')[0], SMS_senderNumber, TP_serviceCenterTimeStamp, message_text))

                    i += 2
                else:
                    i += 1
        return result

    def getGsmLocations(self):
        GSMCGNSInfo = namedtuple("GSMCGNSInfo", [ "latitude", "longitude", "msl_altitude" ])
        ip_address = self.connect_gprs(self.apn)
        if ip_address is False:
            if not keep_session:
                self.disconnect_gprs()
                return False

        cmd = "AT+CLBSCFG=0,1"
        data = self.command_data_ok(cmd)   
        cmd = "AT+CLBSCFG=0,2"
        data = self.command_data_ok(cmd)   
        cmd = "AT+CLBSCFG=0,3"
        data = self.command_data_ok(cmd)   
        cmd = "AT+CLBSCFG=1,3,\"lbs-simcom.com:3002\""
        self.command_ok(cmd)   
        cmd = "AT+CLBS=1,1"
        data = self.command_data_ok(cmd)   

        pattern = r'\+CLBS: (\S+)'
        matches = re.findall(pattern, data)
        if matches:
            coordinates = matches[0].split(',')
            if len(coordinates) == 4:
                mode, longitude, latitude, altitude = coordinates
            else:
                raise Exception(f"getGsmLoctions failed, Not enough coordinates, data: {data}")
        else:
            raise Exception(f"getGsmLoctions failed, Coordinates not found")

        self._Latitude = latitude
        self._Longitude = longitude
        self._Altitude = altitude
        gsm_cgns_info = GSMCGNSInfo(latitude=latitude, longitude=longitude, msl_altitude=altitude)
        
        if not self.disconnect_gprs():
            self.command('AT+HTTPTERM\n')
            self.disconnect_gprs()
            return False        
        
        return(gsm_cgns_info)

    
    def post_get(self, td, api_url):
        rc = self.http(api_url, td.encode(), method="PUT", use_ssl=False, apn=self.apn)
        print(self.http(api_url, method="GET", use_ssl=False, apn=self.apn))    


    def dial_phone_number(self, phone_number):
        buf = None
        rc = self.command_ok('ATD' + phone_number + ';')
        if(rc):
            try:
                while True:
                    while self.ser.inWaiting() > 0:
                        buf = self.ser.readline()
                        buf = buf.decode('gsm03.38', errors="ignore").strip()
                    if buf != None:
                        break 
            except KeyboardInterrupt:
                if self.ser != None:
                    self.ser.close()
        return(buf)

    def responce_phone_call(self):
        buf = ""
        phone_number = ""
        self.ser.flushInput()
        try:
            while True:
                while self.ser.inWaiting() > 0:
                    data = self.ser.readline()
                    buf = data.decode('gsm03.38', errors="ignore").strip()
                    if "RING" in buf:
                        break
                if '+CLIP:' in buf:
                    print(buf)
                    rc = self.command_ok('ATA')
                    split_result = buf.split(',')
                    phone_number = split_result[0].split(': ')[1].strip('"')
                    break;
            while True:
                data = self.ser.readline()
                buf = data.decode('gsm03.38', errors="ignore").strip()
                if buf != None:
                    break 
                time.sleep(1)
            
        except KeyboardInterrupt:
            rc = self.command_ok('ATH')
            if self.ser != None:
                self.ser.close()
        
        return(phone_number)

class Telemetry():
    def __init__(self, rover):
        self.debug = 0
        self.rover = rover

    def get_telemetry_data(self):
        telemetry_data = {
            "Flash ID": self.rover.get_flash_id(),
            "Hw revision": self.rover.get_hw_revision(),
            "Date": self.rover.get_date().strftime('%Y-%m-%d %H:%M:%S'),
            "Operator": self.rover.get_operator(),
            "Service provider": self.rover.get_service_provider(),
            "Signal strength": f"{self.rover.get_signal_strength()}%",
            "Temperature": f"{self.rover.get_temperature()} degrees",
            "MSISDN": self.rover.get_msisdn(),
            "Battery Voltage": f"{self.rover.get_battery_voltage()} V",
            "IMSI": self.rover.get_imsi(),
            "ICCID": self.rover.get_ccid(),
            "Unit Name": self.rover.get_unit_name(),
            "Balance": f"{self.rover.getMtsBalance()} rub.",
            "SIM is registered": self.rover.is_registered()
        }

        try:
            gnss_data = self.rover.get_cgns_data()
            gnss_parsed_data = self.rover.parse_cgns_info(gnss_data)
            gnss_parsed_data = json.loads(gnss_parsed_data)
        
        except Exception as e:
            if "GNSS Position not fixed" in str(e):
                # Обработка исключения, если "GNSS Position not fixed"
                print("Ошибка: GNSS Position не зафиксировано")
                
                gnss_parsed_data = {
                    "GNSS Position not fixed" : 1
                }
            else:
                # Обработка других исключений, если не "GNSS Position not fixed"
                print(f"Произошла ошибка: {e}")
        
        gsm_gnss_data = self.rover.getGsmLocations()
        gsm_gnss_info = gsm_gnss_data
        
        # Создаем словарь на основе данных GSMCGNSInfo
        gsm_gnss_info_data = {
            "latitude": gsm_gnss_info.latitude,
            "longitude": gsm_gnss_info.longitude,
            "msl_altitude": gsm_gnss_info.msl_altitude
        }

        # Преобразуем словарь в JSON-строку
        gsm_gnss_info_json = json.dumps(gsm_gnss_info_data, ensure_ascii=False, indent=2)  
        gsm_gnss_info_json = json.loads(gsm_gnss_info_json)        
       
        combined_data = {
            "sim868cfg": telemetry_data,
            "gnss": gnss_parsed_data,
            "gsm_gnss": gsm_gnss_info_json
        }

        # Преобразуем объединенный JSON в строку
        combined_json = json.dumps(combined_data, ensure_ascii=False, indent=2)        
        
        return combined_json

