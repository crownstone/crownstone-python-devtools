from tools.rssi.RssiNeighbourMessageRecord import RssiNeighbourMessageRecord
from tools.rssi.RssiFeatures import RssiFeatures, RssiChannelFeatures

from datetime import timedelta
from statistics import mean, stdev, median_grouped, variance, StatisticsError
from functools import reduce

class RssiNeighbourMessageAggregator:
    def __init__(self, *args, **kwargs):
        self.verbose = kwargs.get('verbose', False)
        self.dryRun = kwargs.get('dryRun', False)
        self.messageList = []
        self.maxListSize = 5

    def run(self, inFile, outFile):
        """
        loads lines in inFile, extract/aggregate features and print to outFile.
        Comments are forwarded too.
        """
        print("running RssiNeighbourMessageAggregator")
        for line in inFile:
            if line[0] != "#":
                record = RssiNeighbourMessageRecord.fromString(line)
                self.update(record)
                features = self.getFeatures()
                print(str(features), file=outFile)
                if self.verbose:
                    print(str(features))
            else:
                # comments go straight into the next file
                print(line, file=outFile)
                if self.verbose:
                    print(line)

    def update(self, rssiNeighbourMessageRecord):
        """
        Add record to the list, removing oldest entry if necessary.
        """
        self.messageList.append(rssiNeighbourMessageRecord)
        overflow = len(self.messageList) - self.maxListSize
        if overflow >= 0:
            self.messageList = self.messageList[overflow:]

    def getFeatures(self):
        # tail_5 = self.tailByCount(5)
        # tail_10 = self.tailByCount(10)
        # tail_50 = self.tailByCount(50)
        #
        # history_10s = self.tailByTime(10)
        # history_30s = self.tailByTime(30)
        # history_60s = self.tailByTime(60)
        # history_5m = self.tailByTime(60*5)
        #
        # [
        # self.getOutputLine(self.tailByCount(5))
        #     getOutputLine(self.tailByCount(10))
        # ]

        features = self.getFeaturesWithFilter(self.tailByCount(5))
        print(F"cached messages: {len(self.messageList)}, newest entry: {self.messageList[-1]}")
        return features

    def getFeaturesWithFilter(self, preFilter):
        prefilteredMsgs = preFilter(self.messageList) # apply filter
        return RssiFeatures(prefilteredMsgs)

    # filters
    def tailByCount(self, count):
        def filter(inputlist, count):
            return inputlist[-count:]
        return lambda msgs: filter(msgs,count)

    def tailByTime(self, seconds):
        def filter(inputlist, seconds):
            threshold = inputlist[-1].timestamp - timedelta(seconds=seconds)
            return [msg for msg in inputlist if msg.timestamp > threshold]
        return lambda msgs: filter(msgs,seconds)

    # transforms
    def logistic(self, msgList):
        pass

