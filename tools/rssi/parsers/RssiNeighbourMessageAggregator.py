from tools.rssi.RssiNeighbourMessageRecord import RssiNeighbourMessageRecord
from tools.rssi.RssiFeatures import RssiFeatures, RssiChannelFeatures, RssiPrefilteredFeatures

from datetime import timedelta
from itertools import chain
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
        featureExtractors = self.getFeatureExtractors()

        print("running RssiNeighbourMessageAggregator")
        printColumnHeader = True
        for line in inFile:
            if printColumnHeader:
                extractorHeaders = [extractor.columnNames() for extractor in featureExtractors]
                header = ", ".join(list(chain(*extractorHeaders)))
                print(header, file=outFile)
                if self.verbose:
                    print(header)
                printColumnHeader = False

            if line[0] != "#":
                record = RssiNeighbourMessageRecord.fromString(line)
                self.update(record)
                print(F"cached messages: {len(self.messageList)}, newest entry: {self.messageList[-1]}")

                values = []
                for extractor in featureExtractors:
                    extractor.load(self.messageList)
                    currentValue = extractor.valuesCsv()
                    values.append(currentValue)

                    if self.verbose:
                        print(currentValue)

                print(",".join(values), file = outFile)
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

    def getFeatureExtractors(self):
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
        extractors = [
            RssiPrefilteredFeatures("tail5", self.tailByCount(5)),
            RssiPrefilteredFeatures("tail5", self.tailByCount(10))
        ]
        return extractors

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

