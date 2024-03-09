# xbee_gateway

This add-on provides à XBee gateway to send/receive messages
to/from a single XBee or to/from an extended XBee network.

### Integration with Home Assistant 

Communication/integration with Home Assistant is realized 
using 2 MQTT topics. 
- one for HA scripts to send messages
  - topic name proposed is `send_xbee` but is configurable
- another one to handle messages reception and passing them 
back to Home Assistant 
  - topic name proposed is `xbee_received` but is configurable

### Home Assistant requirements

On your Home Assistant you must have configured 2 needed add-ons
- **MQTT (used Mosquito broker in dev/test)**
  - define 2 topics to send and receive messages (by default `send_xbee` and`xbee_received` are proposed)
- **Samba Share**
  - used to update add-on local directory on your Home Assistant installation.

### Configuration example

    XBee_Device: /dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A700e5FD-if00-port0
    XBee_Baud: 115200
    XBee_D2_State: input
    XBee_D2_Level: high
    MQTT_Host: homeassistant.local
    MQTT_Port: 1883
    MQTT_User: mqtt
    MQTT_Password: mqtt
    MQTT_Receive: xbee_received
    MQTT_Send: send_xbee
    ADDON_Logging: INFO

- XBee_Device:
    - /dev/ttyUSBx
    - /dev/ttyACMx
    - /dev/serial/by-id/...... (this one is preferable)
      - it is recommended to use a "by-id" path to the 
      device if one exists, as it is not subject to change if other devices are added
      to the system. 
      - You may find the correct value for this by going to Settings
      -> System -> Hardware and then look for USB details.
- XBee_Baud:
  - serial line baud rate
- MQTT_Receive: 
  - Topic on which add-on will publish received message
- MQTT_Send: 
  - Topic on which Home Assistant will publish message to be sent by the add-on
- ADDON_Logging: 
  - use python logging levels
    - DEBUG, INFO, WARNING, ERROR, CRITICAL

### Dev/Tests environment where the add-on is produced

- Raspberry PI4B using
  - XBee Pro
  - Core 2024.3.0
  - Supervisor 2024.02.1
  - Operating System 12.0
  - Frontend 20240306.0

### Contributors

- see https://github.com/Helios06/xbee_gateway for last release
- See [contributors page](https://github.com/Helios06/xbee_gateway) for a list of contributors.

### MIT License

Copyright (c) 2023-2024  Helios  helios14_75@hotmail.fr

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
