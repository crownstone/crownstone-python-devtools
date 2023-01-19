from crownstone_devtools.rssi.RssiNeighbourMessageRecord import RssiNeighbourMessageRecord
from crownstone_devtools.rssi.RssiFeatures import RssiChannelFeatures, RssiRecordFilterByTime, RssiRecordFilterByCount, RssiRecordFilterByChannelNonZero

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
            RssiRecordFilterByCount("last-record", 1),
            RssiRecordFilterByCount("last-5-records", 5),
            RssiRecordFilterByCount("last-10-records", 10),
            RssiRecordFilterByCount("last-50-records", 50),
            RssiRecordFilterByTime("last-10-seconds", 10),
            RssiRecordFilterByTime("last-30-seconds", 30),
            RssiRecordFilterByTime("last-5-minutes", 60*5),
        ]

        channels = list(range(3)) + [None]
        names = [F"channel-{i}" if i is not None else "all-channels" for i in channels]
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
                # each line, all filters must run to produce their statistics
                try:
                    record = RssiNeighbourMessageRecord.fromString(line)
                    self.update(record) # update cached messageList
                    if self.verbose:
                        print(F"cached messages: {len(self.messageList)}, newest entry: {self.messageList[-1]}")

                    # create csv line
                    columnValues = []
                    for channelfilter in self.channelFilters:
                        for tailfilter in self.tailFilters:
                            # apply filters
                            filteredRecords = self.messageList # start from the cached messageList
                            filteredRecords = channelfilter.run(filteredRecords) # e.g. channel 2
                            filteredRecords = tailfilter.run(filteredRecords) # e.g. last-10-records

                            # obtain statistics (possibly multiple per set of filters)
                            stats = RssiChannelFeatures(channelfilter.channel)
                            stats.load(filteredRecords)
                            statsvalues = stats.values()

                            # append
                            columnValues += statsvalues

                            if self.verbose:
                                print(F"stats: {channelfilter.name}-{tailfilter.name}:",statsvalues, str(stats))
                    outputline = ",".join([str(val) for val in columnValues])

                except ValueError:
                    if self.verbose:
                        errormessage = "Failed to construct RssiNeighbourMessageRecord"
                        print(F"{line} # Error: {errormessage}")
                    outputline = None

            # after parsing line, produce output to file/terminal
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




