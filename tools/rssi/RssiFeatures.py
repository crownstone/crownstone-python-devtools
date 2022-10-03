from tools.rssi.RssiNeighbourMessageRecord import RssiNeighbourMessageRecord
from statistics import mean, stdev, median_grouped, variance, StatisticsError


class RssiChannelFeatures:
    """
    Consists of features depending only on a single channel.
    Features that cannot be computed/constructed are set to "".

    `channel`: 0 based channel id.
    `records`: list of RssiNeighbourMessageRecord instances.
    """
    def __init__(self, channel, records):
        if channel not in range(3):
            raise ValueError("channel id must be 0,1 or 2")

        self.channel = channel
        self.records = self.validRecords(records)
        print(F"Constructing features for channel {self.channel} using {len(self.records)}/{len(records)} samples")

        self.recordCount = len(records)

        # selects the rssi value of the relevant channel
        toRssi = lambda record: record.rssis[self.channel]

        try:
            self.mean = mean(map(toRssi, self.records))
        except StatisticsError:
            self.mean = ""

        try:
            self.stdev = stdev(map(toRssi, self.records))
        except StatisticsError:
            self.stdev = ""

        try:
            self.median_grouped = median_grouped(map(toRssi, self.records))
        except StatisticsError:
            self.median_grouped = ""


    def validRecords(self, records):
        return [rec for rec in records if rec.rssis[self.channel] != 0]

    def messagesDropCount(self, msgList):
        pass

    def columnNames(self):
        """
        Returns a list of member variables that determine how this object will be stringified.
        Elements must exactly match member variable names
        """
        # return ["channel", "recordCount", "mean", "stdev"]
        return ["mean", "stdev"]

    def __str__(self):
        """
        creates a comma separated string based on the column names by looking up
        the values of the member variables with that exact name.
        """
        return ",".join([str(getattr(self, columnname)) for columnname in self.columnNames()])

class RssiFeatures:
    """
    Extracted features of a rssi message recording.
    """
    def __init__(self, rssiRecords):
        """
        rssiRecords: a list of RssiNeighbourMessageRecord from which the features will be extracted.
        """
        print(F"Constructing RssiFeatures from {len(rssiRecords)} messages")
        self.channelFeatures = [RssiChannelFeatures(i, rssiRecords) for i in range(3)]

    def __str__(self):
        return ",".join([F"{{{feature}}}" for feature in self.channelFeatures])

    def columnNames(self):
        columnNamesWithChannelSuffix = [
            [columnName + "_" + str(channFeat.channel)
                for columnName in channFeat.columnNames()]
                    for channFeat in self.channelFeatures]
        return columnNamesWithChannelSuffix

