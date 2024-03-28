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

import time
import logging

from xbee_io        import xbee_io
from threading      import Thread, Lock

class xbee(xbee_io):

    # AT Commands specifications
    Cmd_EnterCmdMode = "+++"
    Cmd_EndOfCommand = "\r"
    Cmd_ATCmdTimeOut = "ATCT64"
    Cmd_EnterCmdChar = "ATCC2B"
    Cmd_XBeeExitCommandMode = "ATCN"

    # Serial Line parameters
    Cmd_SerialLine = "ATNB0,RO3,AP0"
    Cmd_Baud9600 = "ATBD3"
    Cmd_Baud115200 = "ATBD7"

    # XBee Pro AT commands
    Cmd_EndDeviceAssociation = "ATA1"
    Cmd_CoordinatorAssociation = "ATA2"
    Cmd_ApplyChanges = "ATAC"
    Cmd_AssociationIndication = "ATAI"
    Cmd_APIEnable = "ATAP"
    Cmd_ActiveScan = "ATAS"
    Cmd_ADCVoltageReference = "ATAV"
    Cmd_InterfaceDataRate = "ATBD"
    Cmd_CCAThreshold = "ATCA"
    Cmd_CommandSequenceCharacter = "ATCC"
    Cmd_CoordinatorEnable = "ATCE"
    Cmd_Channel = "ATCH"
    Cmd_CommandModeTimeout = "ATCT"
    Cmd_DI0Configuration = "ATD"
    Cmd_DI00Configuration = "ATD0"
    Cmd_DI01Configuration = "ATD1"
    Cmd_DI02Configuration = "ATD2"
    Cmd_DI03Configuration = "ATD3"
    Cmd_DI04Configuration = "ATD4"
    Cmd_DI05Configuration = "ATD5"
    Cmd_DI06Configuration = "ATD6"
    Cmd_DI07Configuration = "ATD7"
    Cmd_DIBConfiguration = "ATD8"
    Cmd_ForceDissociation = "ATDA"
    Cmd_ReceivedSignalStrength = "ATDB"
    Cmd_DestinationAddressHigh = "ATDH"
    Cmd_DestinationAddressLow = "ATDL"
    Cmd_DestinationNode = "ATDN"
    Cmd_DissociationCyclicSleepPeriod = "ATDP"
    Cmd_ACKFailures = "ATEA"
    Cmd_CCAFailures = "ATEC"
    Cmd_EnergyScan = "ATED"
    Cmd_AESEncryptionEnable = "ATEE"
    Cmd_ForcePoll = "ATFP"
    Cmd_SoftwareReset = "ATFR"
    Cmd_GuardTimes = "ATGT"
    Cmd_HardwareVersion = "ATHV"
    Cmd_IOInputAddress = "ATIA"
    Cmd_DIOChangeDetect = "ATIC"
    Cmd_PanId = "ATID"
    Cmd_DigitalOutputLevel = "ATIO"
    Cmd_SampleRate = "ATIR"
    Cmd_ForceSample = "ATIS"
    Cmd_SamplesBeforeTX = "ATIT"
    Cmd_IOOutputEnable = "ATIU"
    Cmd_AESEncryptionKey = "ATKY"
    Cmd_Pwm0OutputLevel = "ATM0"
    Cmd_Pwm1OutputLevel = "ATM1"
    Cmd_MacMode = "ATMM"
    Cmd_SourceAddress = "ATMY"
    Cmd_Parity = "ATNB"
    Cmd_NodeDiscover = "ATND"
    Cmd_NodeIdentifier = "ATNI"
    Cmd_NodeDiscoverTime = "ATNT"
    Cmd_Pwm0Configuration = "ATP0"
    Cmd_Pwm1Configuration = "ATP1"
    Cmd_PowerLevel = "ATPL"
    Cmd_PullUpResistorEnable = "ATPR"
    Cmd_PwmOutputTimeout = "ATPT"
    Cmd_RestoreDefaults = "ATRE"
    Cmd_RandomDelaySlots = "ATRN"
    Cmd_PacketizationTimeOut = "ATRO"
    Cmd_RssiPwmTimer = "ATRP"
    Cmd_XBeeRetries = "ATRR"
    Cmd_ScanChannels = "ATSC"
    Cmd_ScanDuration = "ATSD"
    Cmd_SerialNumberHigh = "ATSH"
    Cmd_SerialNumberLow = "ATSL"
    Cmd_SleepMode = "ATSM"
    Cmd_CyclicSleepPeriod = "ATSP"
    Cmd_TimeBeforeSleep = "ATST"
    Cmd_FirmwareVersionVerbose = "ATVL"
    Cmd_FirmwareVersion = "ATVR"
    Cmd_Write = "ATWR"

    # XBee Pro High level Commands
    Cmd_FastGetParams = "ATCH,BD,HV,VR,ID,SH,SL,PL,DH,DL,MY"
    Cmd_FullInit = "ATMM1,MYFFFF,SP0,RR0,RO3,WR"
    Cmd_ReBoot = "ATFR"
    Cmd_FastCoordinatorAssociation = "ATA27,CE1,WR"
    Cmd_FastCoordinatorDisassociation = "ATA20,CE0,WR"
    Cmd_FastEndDeviceAssociation = "ATA17,CE0,WR"
    Cmd_FastEndDeviceDisassociation = "ATA10,CE0,WR"
    Cmd_Back2Factory = "ATBD7,DH0,DL0,CTFFFF,GT3E8,SD4,EE0,PL4,SC3FC,AP0,NO0,IC0,IR0,SO0,DP3E8,SM0,CA9,RN0,P01,RPFF,AC,WR"
    Cmd_FastApplyChanges = "ATAC,WR"

    def __init__(self, loglevel, name: str, device: str, baud_rate, recv: str, mqtt_client):
        self.XBeeReaderThread = None
        self.MQTTClient = mqtt_client
        self.Ready = False
        self.Name = name
        self.ApiSem = Lock()
        self.Mutex = Lock()
        self.Opened = False
        # set logger
        # DEBUG INFO WARNING ERROR CRITICAL
        # logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
        logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=loglevel)
        xbee_io.__init__(self, loglevel, device, baud_rate)  # since inherited, needs to be called explicitly

    def __del__(self):
        xbee_io.__del__(self)  # since inherited, needs to be called explicitly

    def start(self):
        self.Opened = self.openXBeeIoDevice()
        if self.Opened:
            self.startXBeeIoActivity()
            self.initXBeeDevice()
            self.Ready = True
            self.startXBeeReader()
        else:
            self.Ready = False

    def stop(self):
        if self.Ready:
            self.stopXBeeReader()
            self.stopXBeeIoActivity()
            self.closeXBeeIoDevice()
        self.Ready = False

    def rebootXBeeDevice(self):
        if self.Opened:
            logging.debug("... Reboot XBee device")
            self.ApiSem.acquire()
            self.enterCommandMode()
            self.writeCommandAndWaitOK(self.Cmd_ReBoot)
            time.sleep(1)
            self.ApiSem.release()
            logging.debug("...... Reboot XBee device done")
        else:
            logging.error("Reboot XBee device, device not opened !")

    def changeXBeeDeviceSerialLine(self):
        if self.Opened:
            logging.debug("... Change some Serial Line and Command Parameters")
            self.ApiSem.acquire()
            self.enterCommandMode()
            self.writeCommandAndWaitOK(self.Cmd_EnterCmdChar)
            self.writeCommandAndWaitOK(self.Cmd_ATCmdTimeOut)
            self.writeCommandAndWaitOK(self.Cmd_SerialLine)
            self.writeCommandAndWaitOK(self.Cmd_Baud115200)
            self.writeCommandAndWaitOK(self.Cmd_Write)
            self.exitCommandMode()
            time.sleep(1)
            self.XBeeBaudRate = 115200
            self.ApiSem.release()
            self.stopXBeeIoActivity()
            self.closeXBeeIoDevice()
            self.openXBeeIoDevice()
            self.startXBeeIoActivity()
            logging.debug("...... Change some Serial Line and Command Parameters done")
        else:
            logging.error("Change some Serial Line and Command Parameters, device not opened !")

    def initXBeeDevice(self):
        if self.Opened:
            logging.debug("")
            logging.debug("Init XBee device")
            self.rebootXBeeDevice()
            self.changeXBeeDeviceSerialLine()
            logging.debug("... Get XBee firmware version")
            self.ApiSem.acquire()
            self.enterCommandMode()
            self.writeCommandAndWaitOK(self.Cmd_FirmwareVersionVerbose)
            self.writeCommandAndWaitOK(self.Cmd_Channel)
            self.writeCommandAndWaitOK(self.Cmd_PanId)
            logging.debug("... XBee serial number, source address")
            self.writeCommandAndWaitOK(self.Cmd_SerialNumberHigh)
            self.writeCommandAndWaitOK(self.Cmd_SerialNumberLow)
            time.sleep(0.1)
            logging.debug("... XBee destination address")
            self.writeCommandAndWaitOK(self.Cmd_DestinationAddressHigh + "13A200")
            self.writeCommandAndWaitOK(self.Cmd_DestinationAddressLow + "405C44E2")
            self.writeCommandAndWaitOK(self.Cmd_DestinationAddressHigh)
            self.writeCommandAndWaitOK(self.Cmd_DestinationAddressLow)
            time.sleep(0.1)
            logging.debug("... XBee set MY address")
            self.writeCommandAndWaitOK("ATMYFFFF")  # digital io
            time.sleep(0.1)
            self.setDigitalIOHigh("2")
            time.sleep(1)
            self.setDigitalIOHigh("3")
            time.sleep(0.1)
            self.exitCommandMode()
            self.flushXBeeIoDevice()
            self.ApiSem.release()
            logging.debug("... Init XBee device done")
        else:
            logging.error("Init, XBee device, not opened !")

    def setDigitalIOLow(self, dio: str):
        if self.Opened:
            logging.debug("")
            logging.debug("... set XBee Digital IO "+dio+" low")
            self.writeCommandAndWaitOK(self.Cmd_DI0Configuration+dio+"=4") # output low
            time.sleep(1)
            logging.debug("...... set XBee Digital IO "+dio+" low done")
        else:
            logging.error("... set XBee Digital IO "+dio+" low, not opened !")

    def setDigitalIOHigh(self, dio: str):
        if self.Opened:
            logging.debug("")
            logging.debug("... set XBee Digital IO "+dio+" high")
            self.writeCommandAndWaitOK(self.Cmd_DI0Configuration+dio+"=5") # output high
            time.sleep(1)
            logging.debug("...... set XBee Digital IO "+dio+" high done")
        else:
            logging.error("... set XBee Digital IO "+dio+" high, not opened !")

    # Start activity thread
    def startXBeeReader(self):
        if self.Opened:
            logging.debug("Starting XBee Reader")
            self.XBeeReaderThread            = Thread(target=self.runXBeeReaderThread)
            self.XBeeReaderThread.daemon     = True
            self.XBeeReaderThread.isRunning  = True
            self.XBeeReaderThread.start()
            logging.debug("... XBee Reader started")

    # Stop activity thread
    def stopXBeeReader(self):
        if self.Opened:
            logging.debug("Stopping XBee Reader")
            self.XBeeReaderThread.isRunning = False
            self.XBeeReaderThread.join()
            logging.debug("... XBee Reader stopped")

    def runXBeeReaderThread(self):
        # SMS Reader, will post to MQTT
        while getattr(self.XBeeReaderThread, "isRunning", True):
            #new_sms = self.readData()
            time.sleep(1)

    @staticmethod
    def readData():
        result = ""
        return result

    def sendXBeeMessage(self, channel: str, command: str):
        logging.debug("Sending command to XBee")
        if command == "on":
            self.ApiSem.acquire()
            self.enterCommandMode()
            self.setDigitalIOLow(channel)
            self.exitCommandMode()
            self.ApiSem.release()
        else:
            self.ApiSem.acquire()
            self.enterCommandMode()
            self.setDigitalIOHigh(channel)
            self.exitCommandMode()
            self.ApiSem.release()
        logging.debug("... sending command to XBee, done")