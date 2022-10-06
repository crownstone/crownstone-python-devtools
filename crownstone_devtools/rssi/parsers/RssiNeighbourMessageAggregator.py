from tools.rssi.RssiNeighbourMessageRecord import RssiNeighbourMessageRecord
from tools.rssi.RssiFeatures import RssiChannelFeatures, RssiRecordFilterByTime, RssiRecordFilterByCount, RssiRecordFilterByChannelNonZero

class RssiNeighbourMessageAggregator:
    """
    Parses a csv file consisting of `RssiNeighbourMessageRecord`s using several filters to generate
    basic statistics.
    """
    def __init__(self, *args, **kwargs):
        self.verbose = kwargs.get('verbose', False)
        self.dryRun = kwargs.get('dryRun', False)
        self.messageList = []
        self.maxListSize = 50

        self.tailFilters = [
            RssiRecordFilterByCount("last-5-records", 5),
            RssiRecordFilterByCount("last-10-records", 10),
            RssiRecordFilterByCount("last-50-records", 50),
            RssiRecordFilterByTime("last-10-seconds", 10),
            RssiRecordFilterByTime("last-30-seconds", 30),
            RssiRecordFilterByTime("last-5-minutes", 60*5),
        ]

        channels = list(range(3)) + [None]
        names = [F"channel-{i}" if i else "all-channels" for i in channels]
        self.channelFilters = [
            RssiRecordFilterByChannelNonZero(name, chan)
                for chan,name in zip(channels,names)]

    def run(self, inFile, outFile):
        """
        loads lines in inFile, extract/aggregate features and print to outFile.
        Applies all the combinations of filters.
        Comments are forwarded too.
        """
        if self.verbose:
            print("running RssiNeighbourMessageAggregator")

        printColumnHeader = True
        for line in inFile:
            outputline = None

            if printColumnHeader:
                columnNames = []
                for channelfilter in self.channelFilters:
                    for tailfilter in self.tailFilters:
                        for statisticname in RssiChannelFeatures.columnNames():
                            columnNames.append(F"{channelfilter.name}_{tailfilter.name}_{statisticname}")
                header = ", ".join(columnNames)

                self.output(F"# {header}", outFile)
                printColumnHeader = False

            if line[0] == "#":
                # comments go straight into the next file
                outputline = line
            else:
                try:
                    record = RssiNeighbourMessageRecord.fromString(line)
                    self.update(record)
                    if self.verbose:
                        print(F"cached messages: {len(self.messageList)}, newest entry: {self.messageList[-1]}")

                    # create csv line
                    values = []
                    for channelfilter in self.channelFilters:
                        for tailfilter in self.tailFilters:
                            filteredRecords = self.messageList
                            filteredRecords = channelfilter.run(filteredRecords)
                            filteredRecords = tailfilter.run(filteredRecords)

                            stats = RssiChannelFeatures(channelfilter.channel)
                            stats.load(filteredRecords)
                            statsvalues = stats.values()
                            values += statsvalues
                            if self.verbose:
                                print(F"stats: {channelfilter.name}-{tailfilter.name}:",statsvalues, str(stats))
                    outputline = ",".join([str(val) for val in values])

                except ValueError:
                    if self.verbose:
                        errormessage = "Failed to construct RssiNeighbourMessageRecord"
                        print(F"{line} # Error: {errormessage}")
                    outputline = None

            self.output(outputline, outFile)

    def output(self, outputline, outFile):
        if outputline is not None:
            if not self.dryRun:
                print(outputline, file=outFile)
            if self.verbose:
                print(F"output: {outputline}")

    def update(self, rssiNeighbourMessageRecord):
        """
        Add record to the end the list, removing oldest entry if max capacity is reached.
        """
        self.messageList.append(rssiNeighbourMessageRecord)
        overflow = len(self.messageList) - self.maxListSize
        if overflow >= 0:
            self.messageList = self.messageList[overflow:]




