import logging
import csv
import pdfStamp
import argparse
import json
from pathlib import Path

with open('../log', 'w'):
    pass
logging.basicConfig(filename='../log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", required=True, help="path to the config file")
parser.add_argument("-f", "--file", required=False, help="path to the pdf file")
args = vars(parser.parse_args())

# read configuration file and start stamping
if Path(args["config"]).exists():
	with open (args["config"]) as f:
		configData = json.load(f)
		dataPath = configData["stampDataPath"]
		pdfFiles = dataPath + configData["files"]
		metadata = dataPath + configData["metadata"]
		mode = args["manual"]
	# set file name from args if manual mode is enabled
	if args["file"]:
		if Path(args["file"]).exists():
			originFile = args["file"]
			newDoc = pdfStamp.Document(originFile, configData, 'file')
			newDoc.startPdfParser()
		else:
			print('File not found: ', args["file"])
	# loop through csv file for auto mode
	elif Path(pdfFiles).exists():
		with open (pdfFiles) as fileList:
			names = csv.reader(fileList, delimiter=';', quotechar='#')
			for item in names:
				originFile = '/'.join(item)
				newDoc = pdfStamp.Document(originFile, configData, 'auto')
				newDoc.startPdfParser()
	else:
		print('File not found: ', pdfFiles)
else:
	print('Config file not found: ', args["config"])