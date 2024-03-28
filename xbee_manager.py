"""
MIT License

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
"""

import paho.mqtt.client as mqtt
import sys
import signal
import argparse
import json
import logging

from xbee import xbee


global  xbee_gateway, mqtt_client, options

def signal_handler(sig, frame):
    global  xbee_gateway, mqtt_client

    logging.info('Closing XBee gateway under signal handler')
    xbee_gateway.stop()
    logging.info('... XBee gateway stopped and closed under signal handler')
    sys.exit(0)

def print_response(data):
    for key, value in data["response"].items():
        logging.info(f"   {key}:  {value}")

def on_message(client, userdata, msg):
    global xbee_gateway, mqtt_client, options

    logging.info("")
    logging.info(f"MQTT send message received")
    logging.debug(f"... JSON UTF-8 Message")
    logging.debug(msg.payload)
    message = json.loads(msg.payload)
    if message["channel"].upper() == "DIO0":
        LineLevel = options.l0
    if message["channel"].upper() == "DIO1":
        LineLevel = options.l1
    if message["channel"].upper() == "DIO2":
        LineLevel = options.l2
    if message["channel"].upper() == "DIO3":
        LineLevel = options.l3
    logging.info(f"... channel: %s, LineLevel: %s, command: %s", message["channel"], LineLevel, message["command"])
    xbee_gateway.sendXBeeMessage(LineLevel, message["command"])


def main_modem(loglevel, options):
    global xbee_gateway, mqtt_client

    # Start gateway
    logging.basicConfig(format='%(asctime)s %(message)s')
    logging.info('Starting XBee gateway')
    xbee_gateway = xbee(loglevel, "Huawei", options.device, options.baud_rate, options.recv, mqtt_client)
    xbee_gateway.start()
    while not xbee_gateway.Ready:
        pass

    logging.info('Subscribing on topic: '+options.send)
    mqtt_client.subscribe(options.send)
    logging.info('... Subscribing done')

    logging.info('')
    logging.info('Entering MQTT endless loop')
    mqtt_client.loop_forever()
    logging.info('... Leaving MQTT endless loop')


def main(args=None):
    global mqtt_client, options

    try:
        parser = argparse.ArgumentParser(description="Name Server command line launcher")
        parser.add_argument("-d", "--device", dest="device", help="USB device name", default="/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A700e5FD-if00-port0")
        parser.add_argument("-b", "--baud", dest="baud_rate", help="baud rate", default="115200")
        parser.add_argument("--l0", dest="l0", help="Line 0", default="2")
        parser.add_argument("--l1", dest="l1", help="Line 1", default="3")
        parser.add_argument("--l2", dest="l2", help="Line 2", default="")
        parser.add_argument("--l3", dest="l3", help="Line 3", default="")
        parser.add_argument("-u", "--user", dest="user", help="mqtt user", default="mqtt")
        parser.add_argument("-s", "--secret", dest="secret", help="mqtt user password", default="mqtt")
        parser.add_argument("-r", "--host", dest="host", help="mqtt host", default="homeassistant.local")
        parser.add_argument("-p", "--port", dest="port", help="mqtt port", default="1883")
        parser.add_argument("--send", dest="send", help="mqtt send", default="send_xbee")
        parser.add_argument("--recv", dest="recv", help="mqtt receive", default="xbee_received")
        parser.add_argument("--log", dest="logging", help="addon logging level", default="DEBUG")
        options = parser.parse_args(args)
    except (Exception,):
        return None

    # set logger
    # DEBUG INFO WARNING ERROR CRITICAL
    log_level = logging.DEBUG
    if options.logging == "DEBUG":
        log_level = logging.DEBUG
    if options.logging == "INFO":
        log_level = logging.INFO
    if options.logging == "WARNING":
        log_level = logging.WARNING
    if options.logging == "ERROR":
        log_level = logging.ERROR
    if options.logging == "CRITICAL":
        log_level = logging.CRITICAL

    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=log_level)
    logging.basicConfig(level=log_level)

    logging.info('')
    logging.info('Arguments parsed:')
    logging.info('... device is: '+options.device)
    logging.info('... baud rate is: '+options.baud_rate)
    logging.info('... DIO0 level is DIO: '+options.l0)
    logging.info('... DIO1 level is DIO: '+options.l1)
    logging.info('... DIO2 level is DIO: '+options.l2)
    logging.info('... DIO3 level is DIO: '+options.l3)
    logging.info('... mqtt user is: '+options.user)
    logging.info('... mqtt user secret is: '+options.secret)
    logging.info('... mqtt host is: '+options.host)
    logging.info('... mqtt port is: '+options.port)
    logging.info('... mqtt send is: '+options.send)
    logging.info('... mqtt recv is: '+options.recv)
    logging.info('... addon logging is: '+options.logging)

    # Handle Interrupt and termination signals
    logging.info("")
    logging.info('Preparing signal handling for termination')
    signal.signal(signal.SIGINT, signal_handler)  # Handle CTRL-C signal
    signal.signal(signal.SIGTERM, signal_handler)  # Termination signal
    logging.info('.... signal handling for termination done')

    # Handle MQTT
    logging.info('Connecting to MQTT broker')
    broker = options.host
    port = int(options.port)
    user = options.user
    password = options.secret
    topic = options.send

    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqtt_client.on_message = on_message
    mqtt_client.username_pw_set(user, password)  # see Mosquitto broker config
    # mqtt_client.tls_set()
    mqtt_client.connect(broker)
    logging.info('... Listening to MQTT broker: '+broker+':'+str(port)+' on topic: '+topic)

    main_modem(log_level, options)


if __name__ == '__main__':
    main()
