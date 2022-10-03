from datetime import datetime

class RssiNeighbourMessageRecord:
    """
    a class that encapsulates the records that are logged by the parser (*-raw.csv).
    """
    def __init__(self):
        self.timestamp = None

        self.receiverId = None
        self.senderId = None
        self.rssis = [None] * 3

        # one of these will be set.
        self.msgNumber = None
        self.labelint = None
        self.labelstr = ""

        self.initialized = False

    def loadFromString(self, s):
        vals = s.split(",")
        i = iter(range(10))
        self.timestamp = datetime.fromisoformat(vals[next(i)])
        self.receiverId = int(vals[next(i)])
        self.senderId = int(vals[next(i)])
        self.rssis[0] = int(vals[next(i)])
        self.rssis[1] = int(vals[next(i)])
        self.rssis[2] = int(vals[next(i)])
        self.msgNumber = int(vals[next(i)])
        self.labelint = int(vals[next(i)])
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
                                           self.labelint,
                                           self.labelstr]])
        # return str(self.__dict__)

if __name__ == "__main__":
    s = "2022-07-02T12:16:15.685190,7,6,0,-52,0,132,0, I am not in between A and B"
    r = RssiNeighbourMessageRecord()
    r.loadFromString(s)
    print(str(r.__dict__))