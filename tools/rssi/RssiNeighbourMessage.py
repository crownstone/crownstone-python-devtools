from crownstone_core.util.Conversion import Conversion
from statistics import mean

class RssiNeighbourMessage:
	""" parses raw uart packet into python object and adds a human readible stringificator """
	def __init__(self, payload):
		if len(payload) != 8:
			print("faulty payload")
			self.initialized = False
			return

		self.receiverId = int(payload[1])
		self.senderId = int(payload[2])

		self.rssis = [Conversion.uint8_to_int8(x) for x in payload[3:6]]

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
		return ", ".join([str(x) for x in [self.receiverId, self.senderId, self.rssis[0], self.rssis[1], self.rssis[2], self.msgNumber]])
