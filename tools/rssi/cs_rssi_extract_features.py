import argparse
from pathlib import Path
import os

class FeatureExtractor:
    def __init__(self, inputDirectory, fileNameRegex,  outputDirectory, extractedFileSuffix=None, dryRun=False):
        """
        inputDirectory: where to search for files.
        fileNameRegex: all files whose name matches the regex will have their features extracted.
        outputDirectory: where the extracted files are placed.
        extractedFileSuffix: will be added to the root of the filename. E.g.: myFile.xyz.csv -> myFile.suffix.xyz.csv
        dryRun: if True, script only produces terminal output.
        """
        self.fileNameRegex = fileNameRegex
        self.inputDirectory = inputDirectory or Path('.')
        self.outputDirectory = outputDirectory or self.inputDirectory
        self.extractedFileSuffix = extractedFileSuffix or ".features"
        self.dryRun = bool(dryRun)

        self.inputDirectory = self.validatePath(self.inputDirectory)
        self.outputDirectory = self.validatePath(self.outputDirectory)

    def validatePath(self, p):
        if not p:
            raise FileNotFoundError(F"Path not found: {p}")
        p = p.expanduser()
        if not p.exists():
            raise FileNotFoundError(F"Path not found: {p}")
        return p

    def extractAllFiles(self):
        for p in sorted(self.inputDirectory.glob(self.fileNameRegex)):
            self.extractSingleFile(p)

    def extractSingleFile(self, pathToFile):
        if self.dryRun:
            if not pathToFile.is_file():
                raise ValueError(F"pathToFile is not a file: {pathToFile}")

            head, tail = os.path.split(pathToFile)
            if not tail:
                raise ValueError(F"filename part of path is empty: {pathToFile}")

            tailparts = tail.split(".") # filename and exts
            tailparts[0] += self.extractedFileSuffix
            extendedtail = ".".join(tailparts)
            outputFile = Path(head, extendedtail)

            print(F"extract features of: {pathToFile} into {outputFile}")
            return
        else:
            print("reallly going to to it now!")
            print(F"extract features of: {pathToFile}")

if __name__=="__main__":
    # simple output dir option
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-i", "--inputDirectory", type=Path)
    argparser.add_argument("-o", "--outputDirectory", type=Path)
    argparser.add_argument("-f", "--fileNameRegex", type=str)
    argparser.add_argument("-s", "--extractedFileSuffix", type=str)
    argparser.add_argument("-d", "--dryRun", action='store_true')
    pargs = argparser.parse_args()

    parser = FeatureExtractor(inputDirectory=pargs.inputDirectory,
                              outputDirectory=pargs.outputDirectory,
                              fileNameRegex=pargs.fileNameRegex,
                              extractedFileSuffix=pargs.extractedFileSuffix,
                              dryRun=pargs.dryRun)

    parser.extractAllFiles()
    print("done")
