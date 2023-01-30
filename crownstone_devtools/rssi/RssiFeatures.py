from itertools import chain
from datetime import timedelta
from crownstone_devtools.rssi.RssiNeighbourMessageRecord import RssiNeighbourMessageRecord
from statistics import mean, stdev, median_grouped, multimode


class RssiChannelBasicFeatures:
    """
    Object that computes statistics over a list of RssiNeighbourMessageRecord objects.
    Only includes features that can be constructed based on a single record.
    Features that cannot be computed/constructed are set to "".

    `channel`: 0 based channel id. or None for 'all non-zero values'.
    `records`: list of RssiNeighbourMessageRecord instances.
    """
    def __init__(self):
        self.channel = None
        self.recordCount = None
        self.validRecordCount = None
        self.mean = None
        self.label = None

    def setChannel(self, channel):
        if channel not in range(3) and channel is not None:
            raise ValueError(F"channel id must be 0,1 or 2, got {channel}")

        self.channel = channel

    def load(self, records):
        """
        Reads `records` (a list of RssiNeighbourMessageRecord objects)` and computes statistics.

        All records must be 'valid'.
          - If self.channel is set: all records.rssis[self.channel] != 0 must hold, or
          - Else self.channel is None: at least one rssi value per record must exist.
        """
        self.recordCount = len(records)
        rssis = [self.toRssi(rec) for rec in records]

        if len(rssis) < 1:
            print("too few arguments to compute statistics")
            self.mean = ""
            self.label = ""
        elif len(rssis) == 1:
            rec = records[0]
            rssi = self.toRssi(rec)
            self.mean = rssi
            self.label = rec.labelchr
        else:
            self.mean = mean(rssis)
            # `reversed` ensures priority is given to the last record in tie breaks.
            self.label = multimode(reversed([rec.labelchr for rec in records]))[-1]


    def toRssi(self, record):
        """
        Returns the rssi value of the selected channel or the average of non-zero channels if self.channel is None.
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
        Elements must exactly match member variable names. E.g. "mean" corresponds to self.mean.
        """
        return ["label", "mean"]

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

class RssiChannelExtendedFeatures:
    """
    Object that computes statistics over a list of RssiNeighbourMessageRecord objects.
    Includes features that require multiple records as well as those that can be computed using a single record.
    Features that cannot be computed/constructed are set to "".

    `channel`: 0 based channel id. or None for 'all non-zero values'.
    `records`: list of RssiNeighbourMessageRecord instances.
    """
    def __init__(self):
        self.channel = None
        self.recordCount = None
        self.validRecordCount = None
        self.mean = None
        self.stdev = None
        self.median_grouped = None
        self.label = None
        self.min_max_gap = None

    def setChannel(self, channel):
        if channel not in range(3) and channel is not None:
            raise ValueError(F"channel id must be 0,1 or 2, got {channel}")

        self.channel = channel

    def load(self, records):
        """
        Reads `records` (a list of RssiNeighbourMessageRecord objects)` and computes statistics.

        All records must be 'valid'.
          - If self.channel is set: all records.rssis[self.channel] != 0 must hold, or
          - Else self.channel is None: at least one rssi value per record must exist.
        """
        self.recordCount = len(records)
        rssis = [self.toRssi(rec) for rec in records]

        if len(rssis) < 1:
            print("too few arguments to compute statistics")
            self.mean = ""
            self.stdev = ""
            self.median_grouped = ""
            self.label = ""
            self.min_max_gap = ""
        elif len(rssis) == 1:
            rec = records[0]
            rssi = self.toRssi(rec)
            self.mean = rssi
            self.stdev = ""
            self.median_grouped = rssi
            self.label = rec.labelchr
            self.min_max_gap = ""
        else:
            self.mean = mean(rssis)
            self.stdev = stdev(rssis)
            self.median_grouped = median_grouped(rssis)

            # `reversed` ensures priority is given to the last record in tie breaks.
            self.label = multimode(reversed([rec.labelchr for rec in records]))[-1]

            self.min_max_gap = max(rssis)-min(rssis)

    def toRssi(self, record):
        """
        Returns the rssi value of the selected channel or the average of non-zero channels if self.channel is None.
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
        Elements must exactly match member variable names. E.g. "mean" corresponds to self.mean.
        """
        return ["label", "mean", "stdev", "median_grouped", "min_max_gap"]

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
    def __init__(self, name, seconds, statsGenerator):
        self.name = name
        self.seconds = seconds
        self.statsGenerator = statsGenerator

    def run(self, records):
        if not records:
            return []

        threshold = records[-1].timestamp - timedelta(seconds=self.seconds)
        retval =  [msg for msg in records if msg.timestamp > threshold]

        if len(retval) < 2:
            if len(records) >= 2:
                delta = records[-1].timestamp - records[-2].timestamp
                print("RssiRecordFilterByTime results in less than 2 records! Time between last updates was:", delta)

        return retval

class RssiRecordFilterByCount:
    """
    named object that pre-filters rssi messages. Can be used multiple times by calling run()
    """
    def __init__(self, name, count, statsGenerator):
        self.name = name
        self.count = count
        self.statsGenerator = statsGenerator

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