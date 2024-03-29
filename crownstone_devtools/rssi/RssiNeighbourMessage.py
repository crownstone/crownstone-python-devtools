from crownstone_core.util.Conversion import Conversion
from statistics import mean

class RssiNeighbourMessage:
	""" parses raw uart packet into python object and adds a human readible stringificator """
	def __init__(self, payload=None):
		self.receiverId = None
		self.senderId = None
		self.rssis = [None]*3

		# ideally should log sequential numbers
		self.msgNumber = None

		self.initialized = False

		if payload is None:
			return

		self.loadFromBytes(payload)

	def loadFromBytes(self, payload):
		if len(payload) != 8:
			return

		self.receiverId = int(payload[1])
		self.senderId = int(payload[2])
		self.rssis = [Conversion.uint8_to_int8(x) for x in payload[3:6]]
		self.msgNumber = payload[7]

		self.initialized = True

	def __str__(self):
		if not self.initialized:
			return "# faulty payload!"
		# return self.hexstr
		return ", ".join([str(x) for x in [self.receiverId, self.senderId, self.rssis[0], self.rssis[1], self.rssis[2], self.msgNumber]])


