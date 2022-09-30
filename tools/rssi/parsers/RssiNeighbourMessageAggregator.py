
class RssiNeighbourMessageAggregator:
    def __init__(self):
        self.messageList = []
        self.maxListSize = 50

    def update(self, rssiNeighbourMessageRecord):
        """
        Add record to the list.
        """
        self.messageList.append(rssiNeighbourMessageRecord)
        overflow = len(self.messageList) - self.maxListSize
        if overflow >= 0:
            self.messageList = self.messageList[overflow:]

    # filters
    def getTailByCount(self, count):
        pass

    def getTailByTime(self, timeS):
        pass

    # stats
    def averageFromList(self, msgList):
        pass

    def stdDevFromList(self, msgList):
        pass

    def messageCountFromList(self, msgList):
        pass
