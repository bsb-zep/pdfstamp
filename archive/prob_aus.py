from urllib.request import urlopen
import requests
import re
import csv

with open('meta_error.csv') as f:
	list_oai_err = csv.reader(f, delimiter=',')
	for num in list_oai_err:
		link = num[0] + '/' + num[1]
		url = "https://www.bohemia-online.de/index.php/bohemia/article/download/" + link
		r = urlopen(url)
		fname = r.headers['content-disposition']
		fname = fname.split(';')
		fname = fname[1]
		fname = fname.split('="')
		fname = fname[1]
		fname = fname[:-1]
		fname = fname.split('-')
		out = fname[0] + ',' + fname[1]
		print(out)
