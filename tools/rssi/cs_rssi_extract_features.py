import argparse
from pathlib import Path
import os

from tools.rssi.parsers.RssiNeighbourMessageAggregator import RssiNeighbourMessageAggregator
from tools.rssi.parsers.SenderReceiverFilter import SenderReceiverFilter

class FeatureExtractor:
    # def __init__(self, fileNameRegex, inputDirectory, workDirectory, outputDirectory, parsers, extractedFileSuffix=None, dryRun=False):
    def __init__(self, parsers, *args, **kwargs):
        """
        fileNameRegex: all files whose name matches the regex will have their features extracted.
        inputDirectory: where to search for files.
        workDirectory: where temporary files will be written to.
        outputDirectory: where the extracted files are placed.
        extractedFileSuffix: will be added to the root of the filename. E.g.: myFile.xyz.csv -> myFile.suffix.xyz.csv
        dryRun: if True, script only produces terminal output.
        """
        self.fileNameRegex = kwargs.get("fileNameRegex")
        self.inputDirectory = kwargs.get("inputDirectory", None) or Path('.')
        self.outputDirectory = kwargs.get("outputDirectory",  None) or self.inputDirectory
        self.workDirectory = kwargs.get("workDirectory", None) or self.outputDirectory
        self.extractedFileSuffix = kwargs.get("suffix", ".features")
        self.verbose = kwargs.get("verbose", False)
        self.dryRun = bool(kwargs.get("dryRun", False))

        self.inputDirectory = self.validatePath(self.inputDirectory)
        self.workDirectory = self.validatePath(self.workDirectory)
        self.outputDirectory = self.validatePath(self.outputDirectory)
        self.parsers = parsers

    def validatePath(self, p):
        if not p:
            raise FileNotFoundError(F"Path not found: {p}")
        p = p.expanduser()
        if not p.exists():
                p.mkdir(parents=True)
                print(F"Path not found, calling mkdir -p: {p}")
        return p

    def parseAllFiles(self):
        for p in sorted(self.inputDirectory.glob(self.fileNameRegex)):
            self.parseSingleFile(p)

    def parseSingleFile(self, pathToFile):
        """
        Runs the `parsers` on the given path. Intermediate files are written to the `workDir`.
        """
        if not pathToFile.is_file():
            raise ValueError(F"pathToFile is not a file: {pathToFile}")

        head, tail = os.path.split(pathToFile)
        if not tail:
            raise ValueError(F"filename part of path is empty: {pathToFile}")

        workfilesOut = self.getWorkFilePaths(pathToFile, len(self.parsers))  # out.0, out.1, ...
        workfilesIn = [pathToFile] + workfilesOut[:-1]                       # in,    out.0, out.1, ...

        for index, (parser, inPath, outPath) in enumerate(zip(self.parsers, workfilesIn, workfilesOut)):
            print(F"parsers[{index}].run({inPath}, {outPath})")

            with open(inPath, "r") as inFile:
                with open(outPath, "w+") as outFile:
                    parser.run(inFile,outFile)

        self.moveFileOut(workfilesOut[-1])

    def getWorkFilePaths(self, pathToOriginalFile, count):
        """
        creates an array of paths for the intermediate files.
        They will be in the working directory with an .{index} as suffix.
        """
        if not self.workDirectory.is_dir:
            self.workDirectory.mkdir(parents=True)

        head, tail = os.path.split(pathToOriginalFile)

        # adds the suffix that was set as script arg.
        tailparts = tail.split(".")  # filename and exts
        tailparts[0] += self.extractedFileSuffix
        suffixedtail = ".".join(tailparts)

        return [Path(self.workDirectory, suffixedtail + F".{index}") for index in range(count)]

    def moveFileOut(self, pathToFile):
        """
        moves file to the outDir and strips off its trailing .{index}
        """
        head, tail = os.path.split(pathToFile)
        tail = ".".join(tail.split(".")[:-1])

        outPath = Path(self.outputDirectory,tail)

        if self.verbose:
            print(F"moveFileOut(self, {pathToFile}) -> {outPath}")

        if self.dryRun:
            return

        pathToFile.rename(outPath)

        # opt: remove intermediate files


if __name__=="__main__":
    # simple output dir option
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-i", "--inputDirectory", type=Path)
    argparser.add_argument("-w", "--workDirectory", type=Path)
    argparser.add_argument("-o", "--outputDirectory", type=Path)
    argparser.add_argument("-f", "--fileNameRegex", type=str)
    argparser.add_argument("--suffix", type=str)
    argparser.add_argument("-d", "--dryRun", action='store_true')
    argparser.add_argument("-s", "--sender", type=int)
    argparser.add_argument("-r", "--receiver", type=int)
    argparser.add_argument("-v", "--verbose", default=False, action='store_true')

    pargs = argparser.parse_args()
    print("script args: ", pargs)

    # create parser objects for the pipe line, just passing all command line arguments to constructor
    ioFilter = SenderReceiverFilter(**vars(pargs))
    featureExtractor = RssiNeighbourMessageAggregator(**vars(pargs))
    parserPipeline = FeatureExtractor(parsers=[ioFilter, featureExtractor], **vars(pargs))

    parserPipeline.parseAllFiles()

    print("done")
