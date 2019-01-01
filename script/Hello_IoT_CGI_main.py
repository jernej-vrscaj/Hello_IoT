#!/usr/bin/python3

################################################################################
# Hello_IoT project #
#
# Main CGI file #
# http://IP_ADDRESS/cgi-bin/Hello_IoT_CGI_main.py
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
import subprocess


# Brief: Main HTML page 
# Input args: # fahr: FORMs fahrenheit value 
#             # ntfcn: FORMs notifications value
# Return val: # None
#
def display_cgi_page(fahr = None, ntfcn = None):   
    
    print('''

        <!DOCTYPE html>

        <html>
          <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0"> 
            <title>Hello IoT</title>
            <script type="text/javascript">

                function updateValues(clbk) {
                    var txtFile = new XMLHttpRequest();
                    txtFile.open("GET", "/env_val.txt", true);
                    txtFile.onreadystatechange = function() {
                       if (this.readyState == 4) {
                           if(this.status == 200) {
                               clbk(null, this.responseText);
                           }
                           else {
                              clbk(this.statusText);
                           }
                        }
                    };
                    txtFile.send(null);    
                }

                function callback(err, response) {
                    if(err) {
                        alert("Error: " + err);
                    }
                    else {
                        var resp = response;
                        var n = resp.lastIndexOf("T");
                        var values = resp.slice(n);
                        var arrValues = values.split(",");
                        var chck = arrValues[0].charAt(0);
                        if (chck == "T") {
                            document.getElementById("T").innerHTML = arrValues[0];
                            document.getElementById("H").innerHTML = arrValues[1];
                            document.getElementById("P").innerHTML = arrValues[2];
                        }
                    }
                }

                updateValues(callback);
    ''')
    if ntfcn == 'Notifications':
        print('setInterval(function(){updateValues(callback);}, 1000);')
    print('''            
                

            </script>
            <style>
            * {
            box-sizing: border-box;
            }
            html { 
            background: url(/above_the_clouds_4-wallpaper-1920x1080.jpg) no-repeat center fixed;  
            background-size: cover;
            background-color: rgba(255, 255, 255, 1); /* Used if the image is unavailable */
            height: 100%;
            width: 100%;
            }
            .myfont {
            color: white;
            text-shadow: 1px 1px rgba(0, 0, 0, 1);
            font-family: Trebuchet MS, Helvetica, sans-serif;   
            }
            .window {
            float:left;
            width: 22%;
            }
            .tile {
            font-size: 120%;
            text-align: left;
            background-color: rgba(128, 128, 128, 0.2);
            border: 0px solid gray;
            margin-bottom: 20px;
            padding: 12px;
            display: block;
            width: 100%;
            }
            .btn {
            font-size: 120%;
            text-align: left;
            background-color: rgba(128, 128, 128, 0.2);
            border: 0px solid gray;
            margin-bottom: 20px;
            padding: 12px;
            display: block;
            width: 100%;
            }
            .btn:hover {
            background-color: rgba(128, 128, 128, 0.5);
            cursor: pointer;
            }
            .btn:active {
            background-color: rgba(104, 183, 248, 1);
            cursor: pointer;
            }
            .btn:focus {
            background-color: rgba(104, 183, 248, 1);
            cursor: pointer;
            }
            .switch {
            position: relative;
            display: block;
            width: 60px;
            height: 34px;
            }
            .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(180, 192, 192, 1);
            transition: 0.4s;
            }
            .slider:hover {
            background-color: rgba(128, 128, 128, 1);
            }
            .slider:before {
            position: absolute;
            content: "";
            height: 26px;
            width: 26px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: 0.4s;
            }
            input:checked + .slider {
            background-color: rgba(104, 183, 248, 1);
            }
            input:checked + .slider:before {
            transform: translateX(26px);
            }
            table {
            float: right;
            width: 35%;
            text-align: left;
            font-size: 200%;
            background-color: rgba(128, 128, 128, 0.2);
            border: 0;
            border-collapse: collapse;
            }
            th, td {
            padding: 12px;
            }
            /* Use a media query to add a break point at 768px: */
            @media screen and (max-width:768px) {
            .window, .tile, .btn, table, th, td {
            width: 100%; /* The width is 100%, when the viewport is 768px or smaller */
            }
            }
            </style>
          </head>
          <body> 
            <h1 class="myfont" style="font-size: 300%;">Welcome to the world of IoT!</h1>
            </br>
            </br>
    ''')
    if ntfcn == 'Notifications':
        print('''
                <form action="/cgi-bin/Hello_IoT_CGI_notify.py" method="post">
                <div class="window">
                  <p class="tile myfont">Fahrenheit</p>
                  <label class="switch">
        ''')
        if fahr == 'Fahrenheit':
            print('<input type="checkbox" name="fahrenheit" value="Fahrenheit" checked>')
        else:
            print('<input type="checkbox" name="fahrenheit" value="Fahrenheit">')
        print('''            
                    <span class="slider"></span>
                  </label>
                  <p class="tile myfont">Notifications</p>
                  <p><input class="btn myfont" type="submit" name="notifyON" value="ON"></p>
                  <p><input class="btn myfont" type="submit" name="notifyOFF" value="OFF" formaction="/cgi-bin/Hello_IoT_CGI_main.py"></p>
                  <p><input class="btn myfont" type="submit" name="exitN" value="Exit Notifications" formaction="/cgi-bin/Hello_IoT_CGI_main.py"></p>
                </div>
                </form>
        ''')
    else:
        print('''
                <form action="/cgi-bin/Hello_IoT_CGI_main.py" method="post">
                <div class="window">
                  <p class="tile myfont">Fahrenheit</p>
                  <label class="switch">
        ''')
        if fahr == 'Fahrenheit':
            print('<input type="checkbox" name="fahrenheit" value="Fahrenheit" checked>')
        else:
            print('<input type="checkbox" name="fahrenheit" value="Fahrenheit">')
        print('''            
                    <span class="slider"></span>
                  </label>
                  <p class="tile myfont">Notifications</p>
                  <label class="switch">
                    <input type="checkbox" name="notifications" value="Notifications">
                    <span class="slider"></span>
                    </label>
                    <p><input class="btn myfont" type="submit" name="submit" value="Submit"></p>
                </div>
                </form>
        ''')
    print(''' 
            </br>
            <table class="myfont">
              <tr>
                  <td id="T"></td>
              </tr>
              <tr>
                  <td id="H"></td>
              </tr>
              <tr>
                  <td id="P"></td>
              </tr>
            </table>    
          </body>
        </html>
    ''')
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


# Brief: Save environmental values to .txt file 
# Input args: # v_list: List of characteristic values [temperature, humidity, pressure]
# Return val: # None
#
def save_to_textf(v_list):

    # Clear content on open #
    try:
        fp = open('env_val.txt', 'w', encoding='utf8')

    except IOError as io_exp:
        display_cgi_page_err(io_exp)
        sys.exit()
   
    f_data = v_list[0] + ',' + v_list[1] + ',' + v_list[2]
    fp.write(f_data)

    if not fp.closed:
        fp.close()
####


# Brief: Kill pending notification script with KeyboardInterrupt signal
# Input args: # None
# Return val: # None
#
def kill_ntfcn_pcs():

    subprocess.check_call(['pkill','-SIGINT','-f','/usr/lib/cgi-bin/Hello_IoT_CGI_notify.py'])
####


# Brief: Main
# Input args: # None
# Return val: # None
#
def main():

    # Read values from the FORM #
    formdata = cgi.FieldStorage()
    fahrenheit = formdata.getvalue('fahrenheit')
    notifications = formdata.getvalue('notifications')
    notifyOFF = formdata.getvalue('notifyOFF')
    exitN = formdata.getvalue('exitN')

    # Environmental values #
    temperature = ''
    humidity = ''
    pressure = ''
    val_list = [temperature, humidity, pressure]

    # Directory for the .txt file #
    os.chdir('/var/www/html/')

    # BLE peripheral object #
    periph = btle.Peripheral(None, btle.ADDR_TYPE_RANDOM)

    # Notifications submitted #
    if notifications == 'Notifications':
        display_cgi_page(fahrenheit, notifications)

    # Notifications OFF #
    elif notifyOFF == 'OFF':
        try: 
            kill_ntfcn_pcs()

        except subprocess.CalledProcessError:
            pass

        finally:
            display_cgi_page(fahrenheit, 'Notifications')

    # Exit Notifications menu #
    elif exitN == 'Exit Notifications':
        try:
            kill_ntfcn_pcs()

        except subprocess.CalledProcessError:
            pass

        finally:
            display_cgi_page(fahrenheit)

    # Default #
    else: 
        # Connect to peripheral #
        try:
            periph.connect('D0:65:F1:9B:08:4B', btle.ADDR_TYPE_RANDOM)

        except btle.BTLEDisconnectError as btle_exp:
            try:
                kill_ntfcn_pcs()

            except subprocess.CalledProcessError:
                display_cgi_page_err(btle_exp)
                sys.exit()
 
            display_cgi_page()
            sys.exit()

        finally:
            read_ch_values(periph, fahrenheit, val_list)
            periph.disconnect()
            save_to_textf(val_list)
            display_cgi_page(fahrenheit)
####
    

if __name__ == "__main__":
    main()
