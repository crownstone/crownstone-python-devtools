from crownstone_devtools.rssi.RssiNeighbourMessageRecord import RssiNeighbourMessageRecord

class SenderReceiverFilter:
    """
    Filter that expects a file lines formatted as RssiNeighbourMessageRecord and outputs
    a file in the same format, keeping only the records with matching sender/receiver pairs.
    Use None as wildcard.
    """
    def __init__(self, *args, **kwargs):
        self.sender = kwargs.get('sender', None)
        self.receiver = kwargs.get('receiver', None)
        self.verbose = kwargs.get('verbose', False)
        self.dryRun = kwargs.get('dryRun', False)
        print("SenderReceiverFilter", self.__dict__)

    def run(self, inFile, outFile):
        """
        outputs lines in inPath to outPath if they match sender and receiver.
        Comments, lines starting with a #, are forwarded too.
        """
        print("running SenderReceiverFilter")
        for line in inFile:
            outputline = None

            if line[0] == "#":
                outputline = line
            else:
                try:
                    record = RssiNeighbourMessageRecord.fromString(line)
                    if (self.sender is not None and self.sender != record.senderId) or \
                            (self.receiver is not None and self.receiver != record.receiverId):
                        # skip record, ids don't match
                        outputline = None
                    else:
                        # accept record
                        outputline = str(record)
                except ValueError:
                    if self.verbose:
                        errormessage = "Failed to construct RssiNeighbourMessageRecord"
                        print(F"{line} # Error: {errormessage}")
                    outputline = None

            self.output(outputline,outFile)

    def output(self, outputline, outFile):
        if outputline is not None:
            if not self.dryRun:
                print(outputline, file=outFile)
            if self.verbose:
                print(outputline)