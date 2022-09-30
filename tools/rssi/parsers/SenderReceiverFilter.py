from tools.rssi.RssiNeighbourMessageRecord import RssiNeighbourMessageRecord

class SenderReceiverFilter:
    def __init__(self, *args, **kwargs):
        self.sender = kwargs.get('sender', None)
        self.receiver = kwargs.get('receiver', None)
        print("SenderReceiverFilter", self.__dict__)

    def run(self, inPath, outPath, verbose=False):
        """
        outputs lines in inPath to outPath if they match sender and receiver.
        Comments are forwarded too.
        """
        with open(inPath, "r") as inFile:
            with open(outPath, "a+") as outFile:
                for line in inFile:
                    if line[0] != "#":
                        record = RssiNeighbourMessageRecord.fromString(line)
                        print(record)
                        if (self.sender is not None and self.sender != record.senderId) or \
                                (self.receiver is not None and self.receiver != record.receiverId):
                            # skip irrelevant lines
                            continue
                        else:
                            # output relevant lines to output file
                            print(record, file=outFile)
                            if verbose:
                                print(record)
                    else:
                        # comments go straight into the next file
                        print(line, file=outFile)
                        if verbose:
                            print(line)