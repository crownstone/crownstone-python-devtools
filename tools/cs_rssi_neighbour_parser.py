#!/usr/bin/env python3

"""
This script receives "neighbour rssi" uart messages and logs them to the terminal.
It labels the messages with a time stamp and a short text that describes the physical state
(a la supervised learning).
"""
import time, datetime
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
	def __init__(self):
		self.uartMessageSubscription = UartEventBus.subscribe(SystemTopics.uartNewMessage, self.handleUartMessage)
		self.lastPressed = "None"

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
				print(F"{self.getTimeString()}, {rssiMessage}, {self.lastPressed}")
		except CrownstoneException as e:
			print(f"Parse error: {e}")

	def press(self, key):
		""" ssh keyboard callback """
		self.lastPressed = F"{str(key)}, {self.labels.get(key, 'Unknown label')}"

		print(F"{self.getTimeString()}, keyboard event: {self.lastPressed}")

	def getTimeString(self):
		return datetime.datetime.now().isoformat()





if __name__=="__main__":
	# parser object waits for events of the uart event bus.
	parser = UartRssiMessageParser()

	# Init the Crownstone UART lib.
	uart = CrownstoneUart()
	uart.initialize_usb_sync(port="/dev/ttyACM0")

	# The try except part is just to catch a control+c to gracefully stop the UART lib.
	try:
		listen_keyboard(on_press=lambda k: parser.press(k), until="space")
		print("space was pressed, exiting")
	except KeyboardInterrupt:
		print("\nKeyboardInterrupt received, exiting..")
	finally:
		print("stopping uart")
		uart.stop()
	print("Stopped")