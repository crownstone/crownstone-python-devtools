from tools.rssi.RssiNeighbourMessageRecord import RssiNeighbourMessageRecord

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

    def run(self, inPath, outPath):
        """
        outputs lines in inPath to outPath if they match sender and receiver.
        Comments are forwarded too.
        """
        print("SenderReceiverFilter.run")
        with open(inPath, "r") as inFile:
            with open(outPath, "w+") as outFile:
                for line in inFile:
                    if line[0] != "#":
                        record = RssiNeighbourMessageRecord.fromString(line)
                        if (self.sender is not None and self.sender != record.senderId) or \
                                (self.receiver is not None and self.receiver != record.receiverId):
                            # skip record
                            continue
                        else:
                            # accept record
                            recordstr = str(record)
                            if not self.dryRun:
                                print(recordstr, file=outFile)
                            if self.verbose:
                                print(recordstr)
                    else:
                        # copy comments
                        if not self.dryRun:
                            print(line, file=outFile)
                        if self.verbose:
                            print(line)