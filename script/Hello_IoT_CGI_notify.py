#!/usr/bin/python3

################################################################################
# Hello_IoT project #
#
# Notifications CGI file #
# http://IP_ADDRESS/cgi-bin/Hello_IoT_CGI_notify.py
#
#
################################################################################

# Print output as HTML #
print('Content-Type: text/html \n')

# Import modules #
from bluepy import btle
import cgi
import time
import struct
import sys
import os


# Brief: Callback class for notification events 
# Input args: # valHandle: Tuple of characteristic handle values
#             # fahr: FORMs fahrenheit value 
#             # v_list: List of characteristic values [temperature, humidity, pressure]
# Return val: # None
#
class MyDelegate(btle.DefaultDelegate):

    def __init__(self, valHandle, fahr, v_list):

        btle.DefaultDelegate.__init__(self)
        self.__envHandle = valHandle
        self.__fahr = fahr
        self.__vList = v_list

    def handleNotification(self, cHandle, data):

        if cHandle == self.__envHandle[0]:
            cnv_data = struct.unpack('h', data)
            if self.__fahr == 'Fahrenheit':
                self.__vList[0] = 'T = {0:.2f} °F'.format((cnv_data[0]*0.01)*1.8 + 32.0)
            else:
                self.__vList[0] = 'T = {0:.2f} °C'.format(cnv_data[0]*0.01)
        elif cHandle == self.__envHandle[1]:
            cnv_data = struct.unpack('H', data)
            self.__vList[1] = 'H = {0:.2f} %'.format(cnv_data[0]*0.01)
        elif cHandle == self.__envHandle[2]:
            cnv_data = struct.unpack('I', data)
            self.__vList[2] = 'P = {0:.2f} hPa'.format(cnv_data[0]*0.001)
####


# Brief: Save environmental values to .txt file 
# Input args: # v_list: List of characteristic values [temperature, humidity, pressure]
# Return val: # None
#
def save_to_textf(v_list):

    # Append on open #
    try:
        fp = open('env_val.txt', 'a', encoding='utf8')

    except IOError as io_exp:
        display_cgi_page_err(io_exp)
        sys.exit()

    f_data = v_list[0] + ',' + v_list[1] + ',' + v_list[2] + '\n'
    fp.write(f_data)

    if not fp.closed:
        fp.close()
####


# Brief: Error HTML page 
# Input args: # exp: Raised exception 
# Return val: # None
#   
def display_cgi_page_err(exp):

    print('''

    <!DOCTYPE html>

    <html>
        <head>
            <title>Error</title>
            <script>
            </script>
            <style>
            html { 
            background: url(/Nature___Sundown_Golden_sunset_above_the_clouds_042961_23.jpg) no-repeat center fixed;  
            background-size: cover;
            background-color: rgba(128, 128, 128, 0.4); /* Used if the image is unavailable */
            height: 100%;
            width: 100%;
            }
            .myfont {
            color: white;
            text-shadow: 1px 1px rgba(0, 0, 0, 1);
            font-family: Trebuchet MS, Helvetica, sans-serif;   
            }
            </style>
        </head>
        <body>
        ''')
    print('<p class="myfont" style="font-size: 200%;">Error:',exp,'</p>')
    print('''
        </body>
    </html>

     ''')
####


# Brief: Read characteristic values
# Input args: # sensor: BLE peripheral object 
#             # fahr: FORMs fahrenheit value
#             # v_list: List of characteristic values [temperature, humidity, pressure]
# Return val: # None
#
def read_ch_values(sensor, fahr, v_list):
    
    # Environmental service #
    uuid_svc_env = btle.UUID('0000181a-0000-1000-8000-00805f9b34fb')
    svc_env = sensor.getServiceByUUID(uuid_svc_env)

    # Before reading data, wait some time for sensors to do their readings 
    # and update characteristic values #
    time.sleep(0.2)

    # Read data from Temperature characteristic #
    uuid_ch_temp = btle.UUID('00002a6e-0000-1000-8000-00805f9b34fb')
    ch_temp = svc_env.getCharacteristics(uuid_ch_temp)[0]
    val_temp = ch_temp.read() 
    temp_tuple = struct.unpack('h', val_temp)
    if fahr == 'Fahrenheit':
        v_list[0] = 'T = {0:.2f} °F'.format((temp_tuple[0]*0.01)*1.8 + 32.0)
    else:
        v_list[0] = 'T = {0:.2f} °C'.format(temp_tuple[0]*0.01)
    

    # Read data from Humidity characteristic #
    uuid_ch_humd = btle.UUID('00002a6f-0000-1000-8000-00805f9b34fb')
    ch_humd = svc_env.getCharacteristics(uuid_ch_humd)[0] 
    val_humd = ch_humd.read()
    humd_tuple = struct.unpack('H', val_humd)
    v_list[1] = 'H = {0:.2f} %'.format(humd_tuple[0]*0.01)


    # Read data from Pressure characteristic #
    uuid_ch_press = btle.UUID('00002a6d-0000-1000-8000-00805f9b34fb')
    ch_press = svc_env.getCharacteristics(uuid_ch_press)[0]
    val_press = ch_press.read()
    press_tuple = struct.unpack('I', val_press)
    v_list[2] = 'P = {0:.2f} hPa'.format(press_tuple[0]*0.001)
####


# Brief: Read characteristic notification values
# Input args: # sensor: BLE peripheral object 
#             # fahr: FORMs fahrenheit value
#             # UPDT_INT: Sensor values update interval in connection mode, in seconds
#             # v_list: List of characteristic values [temperature, humidity, pressure]
# Return val: # None
#
def read_ntfcn_values(sensor, fahr, UPDT_INT, v_list):

    read_ch_values(sensor, fahr, v_list)

    save_to_textf(v_list)
    
    # Environmental service #
    uuid_svc_env = btle.UUID('0000181a-0000-1000-8000-00805f9b34fb')
    svc_env = sensor.getServiceByUUID(uuid_svc_env)

    # Setup to turn notifications ON #

    # Temperature char #
    uuid_ch_temp = btle.UUID('00002a6e-0000-1000-8000-00805f9b34fb')
    ch_temp = svc_env.getCharacteristics(uuid_ch_temp)[0]
    
    # Humidity char #
    uuid_ch_humd = btle.UUID('00002a6f-0000-1000-8000-00805f9b34fb')
    ch_humd = svc_env.getCharacteristics(uuid_ch_humd)[0]
    
    # Pressure char #
    uuid_ch_press = btle.UUID('00002a6d-0000-1000-8000-00805f9b34fb')
    ch_press = svc_env.getCharacteristics(uuid_ch_press)[0]
    
    # Tuple of characteristic handle values #
    ch_env_hnd = ch_temp.valHandle, ch_humd.valHandle, ch_press.valHandle

    # Set callback object for notification events #
    sensor.setDelegate(MyDelegate(ch_env_hnd, fahr, v_list))

    # Temperature notification ON #
    sensor.writeCharacteristic(ch_temp.valHandle+1, b'\x01\x00')
    # Humidity notification ON #
    sensor.writeCharacteristic(ch_humd.valHandle+1, b'\x01\x00')
    # Pressure notification ON #
    sensor.writeCharacteristic(ch_press.valHandle+1, b'\x01\x00')
    
 
    while True:
        try:
            if sensor.waitForNotifications(UPDT_INT):
                save_to_textf(v_list)

        except KeyboardInterrupt:
            sys.exit()

        except btle.BTLEDisconnectError as btle_exp:
            display_cgi_page_err(btle_exp)
            sys.exit()
        # Other #
        except Exception as exp:
            display_cgi_page_err(exp)
            sys.exit()
####
   

# Brief: Main
# Input args: # None
# Return val: # None
#
def main():

    # Read values from the FORM #
    formdata = cgi.FieldStorage()
    fahrenheit = formdata.getvalue('fahrenheit')

    # Sensor values update interval in connection mode, in seconds #
    UPDT_INT = 1.0

    # Environmental values #
    temperature = ''
    humidity = ''
    pressure = ''
    val_list = [temperature, humidity, pressure]

    # Directory for the .txt file #
    os.chdir('/var/www/html/')

    # Clear content on open #
    try:
        fp = open('env_val.txt', 'w', encoding='utf8')

    except IOError as io_exp:
        display_cgi_page_err(io_exp)
        sys.exit()

    if not fp.closed:
        fp.close()

    # Connect to peripheral #
    try:
        periph = btle.Peripheral('D0:65:F1:9B:08:4B', btle.ADDR_TYPE_RANDOM)

    except btle.BTLEDisconnectError as btle_exp:
        display_cgi_page_err(btle_exp)
        sys.exit()

    finally:
        read_ntfcn_values(periph, fahrenheit, UPDT_INT, val_list)
####


if __name__ == "__main__":
    main()