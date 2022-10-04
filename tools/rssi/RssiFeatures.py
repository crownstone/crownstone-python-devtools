from itertools import chain
from datetime import timedelta
from tools.rssi.RssiNeighbourMessageRecord import RssiNeighbourMessageRecord
from statistics import mean, stdev, median_grouped, variance, StatisticsError


class RssiChannelFeatures:
    """
    Object that computes statistics over a list of RssiNeighbourMessageRecord objects.
    Features that cannot be computed/constructed are set to "".

    `channel`: 0 based channel id. or None for 'all non-zero values'.
    `records`: list of RssiNeighbourMessageRecord instances.
    """
    def __init__(self, channel):
        if channel not in range(3) and channel is not None:
            raise ValueError(F"channel id must be 0,1 or 2, got {channel}")

        self.channel = channel

        self.recordCount = None
        self.validRecordCount = None
        self.mean = None
        self.stdev = None
        self.median_grouped = None

    def load(self, records):
        self.recordCount = len(records)
        rssis = [self.toRssi(rec) for rec in records]

        if len(rssis) < 2:
            print("too few arguments to compute statistics")
            self.mean = ""
            self.stdev = ""
            self.median_grouped = ""
        else:
            self.mean = mean(rssis)
            self.stdev = stdev(rssis)
            self.median_grouped = median_grouped(rssis)

        if any([val == 0 for val in [self.mean, self.stdev, self.median_grouped]]):
            print("zero value")

    def toRssi(self, record):
        """
        Selects the rssi value of the relevant channel or the average if channel is None.
        """
        if self.channel is not None:
            return record.rssis[self.channel]
        nonzeroes = [rssi for rssi in record.rssis if rssi != 0]
        if nonzeroes:
            return mean(nonzeroes)
        return None

    def messagesDropCount(self, msgList):
        pass

    @staticmethod
    def columnNames():
        """
        Returns a list of member variables that determine how this object will be stringified.
        Elements must exactly match member variable names.
        """
        # return ["channel", "recordCount", "mean", "stdev"]
        return ["mean", "stdev", "median_grouped"]

    def values(self):
        """
        Returns a list with values for the columns
        """
        return [getattr(self, columnname) for columnname in self.columnNames()]

    def __str__(self):
        """
        creates a comma separated string based on the column names by looking up
        the values of the member variables with that exact name.
        """
        return ",".join([str(val) for val in self.values()])

class RssiRecordFilterByTime:
    """
    named object that pre-filters rssi messages. Can be used multiple times by calling run()
    """
    def __init__(self, name, seconds):
        self.name = name
        self.seconds = seconds

    def run(self, records):
        if not records:
            return []

        threshold = records[-1].timestamp - timedelta(seconds=self.seconds)
        retval =  [msg for msg in records if msg.timestamp > threshold]

        if len(retval) < 2:
            if len(records) >= 2:
                delta = records[-1].timestamp - records[-2].timestamp
                print("Filtered too much! Time between last updates was:", delta)

        return retval

class RssiRecordFilterByCount:
    """
    named object that pre-filters rssi messages. Can be used multiple times by calling run()
    """
    def __init__(self, name, count):
        self.name = name
        self.count = count

    def run(self, records):
        if len(records) < self.count:
            return records
        return records[-self.count:]

class RssiRecordFilterByChannelNonZero:
    """
    named object that pre-filters rssi messages. Can be used multiple times by calling run()
    """
    def __init__(self, name, channel):
        self.name = name
        self.channel = channel

    def run(self, records):
        if self.channel is not None:
            return [rec for rec in records if rec.rssis[self.channel] != 0]
        else:
            return [rec for rec in records if any([rssi != 0 for rssi in rec.rssis])]

class RssiRecordFilterLogisticTransform:
    pass #TODO: this might be interesting as rssi values have exponential fall-off