from datetime import datetime

class RssiNeighbourMessageRecord:
    """
    a class that encapsulates the records that are logged by the parser (*-raw.csv).
    """
    def __init__(self):
        # iso standard format for datetime
        self.timestamp = None

        # crownstone ids
        self.receiverId = None
        self.senderId = None

        # values (neg. ints) of the channels 37-39.
        self.rssis = [None] * 3

        # sequence number for administration of message drops
        self.msgNumber = None

        # parameter is a string representation of a key, possibly 'enter', 'space' or 'None'.
        self.labelchr = None

        # value will be a human readible/semantic value corresponding to labelchr
        self.labelstr = ""

        # runtime state, internal use only
        self.initialized = False

    def loadFromString(self, s):
        print(F"s:={s}")
        vals = s.split(",")
        i = iter(range(10))
        self.timestamp = datetime.fromisoformat(vals[next(i)])
        self.receiverId = int(vals[next(i)])
        self.senderId = int(vals[next(i)])
        self.rssis[0] = int(vals[next(i)])
        self.rssis[1] = int(vals[next(i)])
        self.rssis[2] = int(vals[next(i)])
        self.msgNumber = int(vals[next(i)])
        self.labelchr = vals[next(i)]
        self.labelstr = str(vals[next(i)]).strip()
        self.initialized = True
        return self

    @staticmethod
    def fromString(s):
        msg = RssiNeighbourMessageRecord()
        return msg.loadFromString(s)

    def __str__(self):
        return ",".join([str(x) for x in [self.timestamp.isoformat(),
                                           self.receiverId,
                                           self.senderId,
                                           self.rssis[0],
                                           self.rssis[1],
                                           self.rssis[2],
                                           self.msgNumber,
                                           self.labelchr,
                                           self.labelstr]])
        # return str(self.__dict__)

if __name__ == "__main__":
    s = "2022-07-02T12:16:15.685190,7,6,0,-52,0,132,0, I am not in between A and B"
    r = RssiNeighbourMessageRecord()
    r.loadFromString(s)
    print(str(r.__dict__))