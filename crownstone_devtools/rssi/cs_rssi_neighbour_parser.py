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

from crownstone_devtools.rssi.RssiNeighbourMessage import RssiNeighbourMessage


class UartRssiMessageParser:
	def __init__(self, outputDirectory, workingDirectory, logToFile=True, verbose=False):
		"""
		logToFile: if false, script only produces terminal output, otherwise a logfile is created.
		workingDirectory: as long as a log file is actively written to, it will be kept here
		outputDirectory: when a log file is complete it is copied to this dir. (happens when a new log file is created)
		"""
		self.uartMessageSubscription = UartEventBus.subscribe(SystemTopics.uartNewMessage, self.handleUartMessage)

		self.logToFile = logToFile
		self.verbose = verbose
		self.logFileName = None

		self.not_labeled = "not labeled"
		self.lastPressed = self.not_labeled

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
			"enter": "# start experiment",
			"space": "# stop experiment",
			"backspace": self.not_labeled,

			"0": "I am not in between A and B",
			"1": "I am in between A and B",

			"2": "I am not home",
			"3": "I am home",

			"4": "Reserved label: 4",
			"5": "Reserved label: 5",
			"6": "Reserved label: 6",
			"7": "Reserved label: 7",
			"8": "Reserved label: 8",
			"9": "Reserved label: 9",

			"a": "I am in room: a",
			"b": "I am in room: b",
			"c": "I am in room: c",
			"d": "I am in room: d",
			"e": "I am in room: e",
			"f": "I am in room: f",
			"g": "I am in room: g",
			"h": "I am in room: h",
			"i": "I am in room: i",
			"j": "I am in room: j",
			"k": "I am in room: k",
			"l": "I am in room: l",
			"m": "I am in room: m",
			"n": "I am in room: n",
			"o": "I am in room: o",
			"p": "I am in room: p",
			"q": "I am in room: q",
			"r": "I am in room: r",
			"s": "I am in room: s",
			"t": "I am in room: t",
			"u": "I am in room: u",
			"v": "I am in room: v",
			"w": "I am in room: w",
			"x": "I am in room: x",
			"y": "I am in room: y",
			"z": "I am in room: z",
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
		self.lastPressed = F"{str(key)}, {self.labels.get(key, self.not_labeled)}"
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
		if not silent or self.verbose:
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
	argparser.add_argument("-v", "--verbose", action='store_true')
	argparser.add_argument("--no_uart", action='store_true')
	argparser.add_argument("--no_escape", action='store_true')
	pargs = argparser.parse_args()

	print(F"""
	esc: {"disabled by script parameter 'no_escape'" if pargs.no_escape else "quit the script (hotkey can be disabled with script parameter 'no_escape')"}
	enter: label start experiment
	space: label stop experiment
	backspace: clear current label
	
	0: not in between
	1: in between
	2: not home
	3: home
	4-9: reserved but functional extra labels 
	a-z: room ids
	""")

	# parser object waits for events of the uart event bus.
	outDir = pargs.outputDirectory or Path('.')
	workDir = pargs.workingDirectory or outDir
	parser = UartRssiMessageParser(outputDirectory=outDir, workingDirectory=workDir, logToFile=pargs.logToFile, verbose=pargs.verbose)

	if pargs.port:
		portname = pargs.port
	else:
		portname = "/dev/ttyACM0"
		if platform.uname().system == 'Windows':
			import serial.tools.list_ports as port_list
			ports = list(port_list.comports())
			# bind to the first COM port and hope it is the right one...
			portname = ports[0].name

	uart = None
	if pargs.no_uart == False:
		# Init the Crownstone UART lib.
		uart = CrownstoneUart()
		uart.initialize_usb_sync(port=portname)

	# The try except part is just to catch a control+c to gracefully stop the UART lib.

	try:
		if os.isatty(sys.stdin.fileno()):
			listen_keyboard(on_press=lambda k: parser.press(k), until=None if pargs.no_escape else "esc")
			print("space was pressed, exiting")
		else:
			while True:
				time.sleep(1)
	except KeyboardInterrupt:
		print("\nKeyboardInterrupt received, exiting..")
	finally:
		print("stopping parser")
		parser.finish()

		if uart:
			print("stopping uart")
			uart.stop()

	print("Stopped")
