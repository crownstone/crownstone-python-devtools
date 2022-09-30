from tools.rssi.RssiNeighbourMessageRecord import RssiNeighbourMessageRecord

class RssiNeighbourMessageAggregator:
    def __init__(self, *args, **kwargs):
        self.verbose = kwargs.get('verbose', False)
        self.dryRun = kwargs.get('dryRun', False)
        self.messageList = []
        self.maxListSize = 5

    def run(self, inFile, outFile):
        """
        loads lines in inPath, extract/aggregate features and send to outPath.
        Comments are forwarded too.
        """
        print("running RssiNeighbourMessageAggregator")
        for line in inFile:
            if line[0] != "#":
                record = RssiNeighbourMessageRecord.fromString(line)
                self.update(record)
                print(self.getOutputLine(), file=outFile)
                if self.verbose:
                    print(self.getOutputLine())
            else:
                # comments go straight into the next file
                print(line, file=outFile)
                if self.verbose:
                    print(line)

    def getOutputLine(self):
        return F"cached messages: {len(self.messageList)}, newest entry: {self.messageList[-1]}"

    def update(self, rssiNeighbourMessageRecord):
        """
        Add record to the list, removing oldest entry if necessary.
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
