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
from sshkeyboard import listen_keyboard

from crownstone_core.Exceptions import CrownstoneException
from crownstone_uart import UartEventBus, UartTopics
from crownstone_uart import CrownstoneUart
from crownstone_uart.core.uart.UartTypes import UartRxType, UartMessageType
from crownstone_uart.core.uart.uartPackets.UartMessagePacket import UartMessagePacket
from crownstone_uart.topics.SystemTopics import SystemTopics

from tools.rssi.RssiNeighbourMessage import RssiNeighbourMessage


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
				self.log(F"{self.getCurrentTimeString()},{rssiMessage},{self.lastPressed}")
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
		rebooted = not self.logFileName

		self.logfileStartTime = datetime.datetime.today()
		self.logFileName = self.logfileStartTime.strftime('NeighborRssiLog_%Y-%m-%d_%Hh%M.csv')
		print(F"updated logfilename to: {self.logFileName}")

		if rebooted:
			self.log("device rebooted")


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
		elif datetime.datetime.today() > self.logfileStartTime + datetime.timedelta(seconds=3600*12):
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
