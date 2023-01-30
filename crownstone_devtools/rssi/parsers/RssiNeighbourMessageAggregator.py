from crownstone_devtools.rssi.RssiNeighbourMessageRecord import RssiNeighbourMessageRecord
from crownstone_devtools.rssi.RssiFeatures import RssiChannelBasicFeatures, RssiChannelExtendedFeatures, RssiRecordFilterByTime, RssiRecordFilterByCount, RssiRecordFilterByChannelNonZero

class RssiNeighbourMessageAggregator:
    """
    Parses a csv file consisting of `RssiNeighbourMessageRecord`s using several filters to generate
    basic statistics.
    """
    def __init__(self, *args, **kwargs):
        self.verbose = kwargs.get('verbose', False)
        self.debug = kwargs.get('debug', False)
        self.dryRun = kwargs.get('dryRun', False)
        self.allowIncompleteRecords = kwargs.get('allowIncompleteRecords',False)

        self.messageList = []
        self.maxListSize = 50

        self.tailFilters = [
            RssiRecordFilterByCount("last-1-record", 1, RssiChannelBasicFeatures()),
            RssiRecordFilterByCount("last-5-records", 5, RssiChannelExtendedFeatures()),
            RssiRecordFilterByCount("last-10-records", 10, RssiChannelExtendedFeatures()),
            RssiRecordFilterByCount("last-50-records", 50, RssiChannelExtendedFeatures()),
            RssiRecordFilterByTime("last-10-seconds", 10, RssiChannelExtendedFeatures()),
            RssiRecordFilterByTime("last-30-seconds", 30, RssiChannelExtendedFeatures()),
            RssiRecordFilterByTime("last-5-minutes", 60*5, RssiChannelExtendedFeatures()),
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
            print("Running RssiNeighbourMessageAggregator")

        printColumnHeader = True
        for lineindex, line in enumerate(inFile):
            outputline = None

            if printColumnHeader:
                columnNames = []
                for channelfilter in self.channelFilters:
                    for tailfilter in self.tailFilters:
                        for statisticname in tailfilter.statsGenerator.columnNames():
                            columnNames.append(F"{channelfilter.name}_{tailfilter.name}_{statisticname}")
                header = ", ".join(columnNames)

                self.output(F"# {header}", outFile)
                printColumnHeader = False

            if self.verbose:
                # adding 1 to index because most spreadsheet editors start counting at 1.
                print("")
                print(F"parsing line #{lineindex + 1}: {line.strip()}")
                print(F"cached messages: {len(self.messageList)}")

            if not line.strip() or line[0] == "#":
                # comments and empty lines go straight into the next file
                outputline = line
            else:
                # each line, all filters must run to produce their statistics
                try:

                    record = RssiNeighbourMessageRecord.fromString(line)
                    if self.verbose:
                        print(F"extracted record: {record.__dict__}")

                    self.update(record) # update cached messageList

                    # create csv line
                    columnValues = []
                    for channelfilter in self.channelFilters:
                        for tailfilter in self.tailFilters:
                            # apply filters
                            filteredRecords = self.messageList # start from the cached messageList
                            filteredRecords = channelfilter.run(filteredRecords) # e.g. channel 2
                            filteredRecords = tailfilter.run(filteredRecords) # e.g. last-10-records

                            # obtain statistics (possibly multiple per set of filters)
                            statsGen = tailfilter.statsGenerator
                            statsGen.setChannel(channelfilter.channel)
                            statsGen.load(filteredRecords)
                            statsvalues = statsGen.values()

                            # append
                            columnValues += statsvalues

                            if self.verbose:
                                print(F"stats: {channelfilter.name}-{tailfilter.name}:", dict(zip(statsGen.columnNames(), statsvalues)))
                    outputline = ",".join([str(val) for val in columnValues])

                except ValueError as e:
                    errormessage = "Failed to construct RssiNeighbourMessageRecord"
                    print(F"Error: {errormessage}")
                    print(e)
                    print(F"line: \'{line}\'")

                    if self.debug:
                        raise

                    outputline = None

            # after parsing line, produce output to file/terminal
            self.output(outputline, outFile)

    def output(self, outputline, outFile):
        if self.verbose:
            print(F"output: '{outputline}'")

        if outputline is None:
            return

        allValuesAreDefined = all(outputline.split(","))
        if not self.allowIncompleteRecords and not allValuesAreDefined:
            print("*** skipping incomplete record ***")
            return

        if not self.dryRun:
            print(outputline, file=outFile)

    def update(self, rssiNeighbourMessageRecord):
        """
        Add record to the end the list, removing oldest entry if max capacity is reached.
        """
        self.messageList.append(rssiNeighbourMessageRecord)
        overflow = len(self.messageList) - self.maxListSize
        if overflow >= 0:
            self.messageList = self.messageList[overflow:]




