import logging
import csv
import pdfStamp

with open('../output/log.log', 'w'):
    pass
logging.basicConfig(filename='../output/log.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

fileList = '../../../fileList.csv'
metadata = '../../../oai_last.csv'
try:
    with open(fileList) as kurz:
        names = csv.reader(kurz, delimiter=',', quotechar='#')
        for fn in names:
            originName = fn[3]
            newDoc = pdfStamp.Document(originName, metadata)
            newDoc.startPdfParser()

except (SystemExit, KeyboardInterrupt):
    raise
except Exception as e:
    if fileList in str(e):
        print('CSV file is not found: ' + fileList, e)
