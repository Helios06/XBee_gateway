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

from    threading   import Thread, Lock
import  serial
import  serial.tools.list_ports
import  time
import  logging

class xbee_io:

    def __init__(self, loglevel, device, baud_rate):
        self.XBeeSerial              = serial.Serial()
        self.XBeeDevice              = device
        self.XBeeBaudRate            = baud_rate
        self.XBeeIoProtocolSem       = Lock()
        self.XBeeIoReadyToSend       = True
        self.CommandSem              = Lock()
        self.WaitingOk               = False
        self.XBeeIoActivityThread    = None
        self.Opened                  = False
        self.XBeeIoOKReceived        = False
        self.XBeeIoFrameReceived     = ""
        # logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
        logging.basicConfig(level=loglevel)

    def __del__(self):
        if self.Opened:
            self.XBeeSerial.close()
        del self.XBeeSerial
        del self.XBeeIoProtocolSem
        del self.CommandSem

    def openXBeeIoDevice(self):
        try:
            logging.info('...... trying to open device on '+self.XBeeDevice)
            self.XBeeSerial.baudrate = self.XBeeBaudRate
            self.XBeeSerial.port = self.XBeeDevice
            self.XBeeSerial.parity = serial.PARITY_NONE
            self.XBeeSerial.bytesize = serial.EIGHTBITS
            self.XBeeSerial.stopbits = serial.STOPBITS_ONE
            self.XBeeSerial.xonxoff = False
            self.XBeeSerial.rtscts = False
            self.XBeeSerial.dsrdtr = False
            self.XBeeSerial.open()
            self.XBeeSerial.flush()
            if self.XBeeSerial.is_open:
                self.Opened = True
                logging.info('......... device is opened on '+self.XBeeDevice)
            else:
                self.Opened = False
                logging.error('......... device is still closed, could not open '+self.XBeeDevice)
        except (Exception,) as e:
            logging.error('......... device exception while opening '+self.XBeeDevice)
            logging.error(e)
        return  self.Opened

    def closeXBeeIoDevice(self):
        logging.info('...... trying to close XBee device')
        self.XBeeSerial.close()
        if self.XBeeSerial.is_open:
            logging.error('......... XBee is still opened ')
        else:
            self.Opened = False
            logging.info('......... XBee is closed ')

    def flushXBeeIoDevice(self):
        self.XBeeSerial.flush()

    def enterCommandMode(self):
        # frame is bytes
        self.XBeeIoOKReceived = False
        frame = bytes(self.Cmd_EnterCmdMode, 'ascii')
        self.writeData(frame)
        while not self.XBeeIoOKReceived:
            time.sleep(0.01)

    def exitCommandMode(self):
        self.writeCommandAndWaitOK(self.Cmd_XBeeExitCommandMode)

    def writeCommandAndWaitOK(self, frame: bytes):
        # frame is bytes
        self.XBeeIoOKReceived = False
        self.writeData(bytes(frame, 'ascii'))
        self.writeData(bytes(self.Cmd_EndOfCommand, 'ascii'))
        while not self.XBeeIoOKReceived:
            time.sleep(0.05)

    def writeData(self, frame: bytes):
        self.XBeeSerial.write(frame)

    # Start activity thread
    def startXBeeIoActivity(self):
        if self.Opened:
            self.XBeeIoActivityThread            = Thread(target=self.runXBeeIoActivityThread)
            self.XBeeIoActivityThread.daemon     = True
            self.XBeeIoActivityThread.isRunning  = True
            self.XBeeIoActivityThread.start()

    # Stop activity thread
    def stopXBeeIoActivity(self):
        if self.Opened:
            self.XBeeIoActivityThread.isRunning = False
            self.XBeeIoActivityThread.join()

    def runXBeeIoActivityThread(self):
        frame: bytes = b''
        while getattr(self.XBeeIoActivityThread, "isRunning", True):
            time.sleep(0.001)
            if self.XBeeSerial.in_waiting >= 1:
                # some data available
                data: bytes = self.XBeeSerial.read(1)
                # logging.debug(data)
                frame += data
                if 'OK\r' in frame.decode("ascii"):
                    # received response
                    self.XBeeIoOKReceived = True
                    self.XBeeIoFrameReceived = frame
                    logging.info(f'............... frame received: %s', frame)
                    frame = b''
                elif '\r' in frame.decode("ascii"):
                    # received response
                    self.XBeeIoOKReceived = True
                    self.XBeeIoFrameReceived = frame
                    logging.info(f'............... frame received: %s', frame)
                    frame = b''
                else:
                    pass
            else:
                pass
