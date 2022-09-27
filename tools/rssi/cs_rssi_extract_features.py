import argparse
from pathlib import Path

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
        self.outputDirectory = outputDirectory or inputDirectory
        self.extractedFileSuffix = extractedFileSuffix
        self.dryRun = bool(dryRun)

        self.validatePath(inputDirectory)
        self.validatePath(outputDirectory)



    def validatePath(self, p):
        if not p.exists():
            raise FileNotFoundError(str(p))

if __name__=="__main__":
    # simple output dir option
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-i", "--intputDirectory", type=Path)
    argparser.add_argument("-o", "--outputDirectory", type=Path)
    argparser.add_argument("-f", "--fileNameRegex", type=str)
    argparser.add_argument("-s", "--extractedFileSuffix", type=str)
    argparser.add_argument("-s", "--dryRun", action='store_false')
    pargs = argparser.parse_args()

    parser = FeatureExtractor(inputDirectory=pargs.inputDirectory,
                              outputDirectory=pargs.outputDirectory,
                              fileNameRegex=pargs.fileNameRegex,
                              extractedFileSuffix=pargs.extractedFileSuffix,
                              dryRun=pargs.dryRun)

    print("done")
