#!/usr/bin/env python3

"""
This script receives "neighbour rssi" uart messages and logs them to file and the terminal.
It labels the messages with a time stamp and a short text that describes the physical state
(a la supervised learning).
"""
import time, datetime
import platform
import argparse
import sys, os
from pathlib import Path

from statistics import mean
from sshkeyboard import listen_keyboard

from crownstone_core.Exceptions import CrownstoneException
from crownstone_core.util.Conversion import Conversion

from crownstone_uart import UartEventBus, UartTopics
from crownstone_uart import CrownstoneUart

from crownstone_uart.core.uart.UartTypes import UartRxType, UartMessageType
from crownstone_uart.core.uart.uartPackets.UartMessagePacket import UartMessagePacket

from crownstone_uart.topics.SystemTopics import SystemTopics

class RssiNeighbourMessage:
	""" parses raw uart packet into python object and adds a human readible stringificator """
	def __init__(self, payload):
		if len(payload) != 8:
			print("faulty payload")
			self.initialized = False
			return

		self.receiverId = int(payload[1])
		self.senderId = int(payload[2])

		# average of non-zero channel values. (there should be only 1 channel non zero anyway)
		self.rssi = mean([Conversion.uint8_to_int8(x) for x in payload[3:6] if x != 0])

		# channel id: 37, 38 or 39 if any is non-zero, else 0
		self.chan = next((i+37 for i, x in enumerate(payload[3:6]) if x), 0) 

		# should be 0 for the tripwire experiment
		self.lastSeenSecondsAgo = payload[6]

		# ideally should log sequential numbers
		self.msgNumber = payload[7]

		self.hexstr = ", ".join(["0x{:02X}".format(x) for x in payload])
		self.initialized = True

	def __str__(self):
		if not self.initialized:
			return "<< faulty payload >>"
		# return self.hexstr
		return ", ".join([str(x) for x in [self.receiverId, self.senderId, self.rssi, self.chan, self.msgNumber]])

class UartRssiMessageParser:
	def __init__(self, outputDirectory, workingDirectory, logToFile=True):
		"""
		logToFile: if false, script only produces terminal output, otherwise a logfile is created.
		workingDirectory: as long as a log file is actively written to, it will be kept here
		outputDirectory: when a log file is complete it is copied to this dir. (happens when a new log file is created)
		"""
		self.uartMessageSubscription = UartEventBus.subscribe(SystemTopics.uartNewMessage, self.handleUartMessage)
		self.lastPressed = None
		self.logFileName = None

		self.logToFile = logToFile

		if outputDirectory.exists():
			print(F"setting outputdir to: {outputDirectory}")
			self.outputDirectory = outputDirectory
		else:
			print(F"outputdir not found, using . instead")
			self.outputDirectory = Path(".")


		if workingDirectory.exists():
			print(F"setting workdir to: {workingDirectory}")
			self.workingDirectory = workingDirectory
		else:
			print(F"workdir not found, using . instead")
			self.workingDirectory = Path(".")

		self.logfileStartTime = None # defined in updateLogFilename
		self.updateLogFilename()

		# a bunch of predefined labels to give semantic meaning to incoming uart messages.
		# the last call to press() determines which of these will be added to the log when receiving a uart msg.
		self.labels = {
			"0": "I am not in between A and B",
			"1": "I am in between A and B",

			"2": "I am not home",
			"3": "I am home",
		}

	def handleUartMessage(self, messagePacket: UartMessagePacket):
		try:
			if messagePacket.opCode == UartRxType.NEIGHBOUR_RSSI:
				rssiMessage = RssiNeighbourMessage(messagePacket.payload)
				self.log(F"{self.getCurrentTimeString()}, {rssiMessage}, {self.lastPressed}")
		except CrownstoneException as e:
			self.log(f"Parse error: {e}")

	def press(self, key):
		""" ssh keyboard callback """
		self.lastPressed = F"{str(key)}, {self.labels.get(key, 'Unknown label')}"
		self.log(F"{self.getCurrentTimeString()}, keyboard event: {self.lastPressed}")

	def getCurrentTimeString(self):
		""" extracted method for uniform formatting. change style here and all logs will be updated. """
		return datetime.datetime.now().isoformat()

	def updateLogFilename(self):
		""" update logfile name and accompanying start date """
		self.logfileStartTime = datetime.datetime.today()
		self.logFileName = self.logfileStartTime.strftime('NeighborRssiLog_%Y-%m-%d_%Hh%M.csv')
		print(F"updated logfilename to: {self.logFileName}")

	def latchLogfileFromWorkToOutputDir(self):
		""" moves current working log file from the work dir to the output dir, possibly overwriting a previous file """
		os.replace(self.workingDirectory / self.logFileName, self.outputDirectory / self.logFileName)

	def getLogFilename(self):
		"""
		returns the path and name to the active/working log file.
		will (re)generate the string when it isn't set yet, or date has changed,
		and latch the working file to the output dir when necessary.
		"""
		if not self.logFileName:
			self.updateLogFilename()
			self.log("device rebooted")
		elif datetime.datetime.today() > self.logfileStartTime + datetime.timedelta(seconds=60*1): # 3600*12
			self.latchLogfileFromWorkToOutputDir()
			self.updateLogFilename()

		return self.logFileName

	def log(self, logstr, silent=False):
		""" logs given string to the current log file. set silent to True to prevent a print to std out. """
		if self.logToFile:
			with open(self.workingDirectory / self.getLogFilename(), "a+") as logfile:
				print(logstr, file=logfile)
		if not silent:
			print(logstr)

	def finish(self):
		""" cleans up working dir by moving last log file to the output dir. """
		self.latchLogfileFromWorkToOutputDir()


if __name__=="__main__":
	# simple output dir option
	argparser = argparse.ArgumentParser()
	argparser.add_argument("-o", "--outputDirectory", type=Path)
	argparser.add_argument("-w", "--workingDirectory", type=Path)
	argparser.add_argument("-p", "--port", type=str)
	argparser.add_argument("-l", "--logToFile", action='store_false')
	pargs = argparser.parse_args()

	# parser object waits for events of the uart event bus.
	outDir = pargs.outputDirectory or Path('.')
	workDir = pargs.workingDirectory or outDir
	parser = UartRssiMessageParser(outputDirectory=outDir, workingDirectory=workDir, logToFile=pargs.logToFile)

	# Init the Crownstone UART lib.
	uart = CrownstoneUart()

	if pargs.port:
		portname = pargs.port
	else:
		portname = "/dev/ttyACM0"
		if platform.uname().system == 'Windows':
			import serial.tools.list_ports as port_list
			ports = list(port_list.comports())
			# bind to the first port...
			portname = ports[0].name

	uart.initialize_usb_sync(port=portname)

	# The try except part is just to catch a control+c to gracefully stop the UART lib.
	try:
		if os.isatty(sys.stdin.fileno()):
			listen_keyboard(on_press=lambda k: parser.press(k), until="space")
			print("space was pressed, exiting")
		else:
			while True:
				time.sleep(1)
	except KeyboardInterrupt:
		print("\nKeyboardInterrupt received, exiting..")
	finally:
		print("stopping parser")
		parser.finish()
		print("stopping uart")
		uart.stop()
	print("Stopped")
