import logging
import csv
import pdfStamp
import argparse
import json
from pprint import pprint


with open('../log', 'w'):
    pass
logging.basicConfig(filename='../log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", required=True, help="path to the config file")
parser.add_argument("-m", "--manual", required=False, help="path to the pdf file")
args = vars(parser.parse_args())

try:
	with open (args["config"]) as f:
		configFile = json.load(f)
		pdfFiles = configFile["files"]
		metadata = configFile["metadata"]
		fileName = args["manual"]
		try:
			with open(pdfFiles) as fileList:
				names = csv.reader(fileList, delimiter=';', quotechar='#')
				for fn in names:
					originName = fn[3]
					newDoc = pdfStamp.Document(originName, metadata)
					newDoc.startPdfParser()

		except (SystemExit, KeyboardInterrupt):
			raise
		except Exception as e:
			if fileList in str(e):
			    print(e)
				
except (SystemExit, KeyboardInterrupt):
    raise
except Exception as e:
    if args["config"] in str(e):
        print(e)
