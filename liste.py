import csv

with open('files_all.csv') as liste:
	names = csv.reader(liste, delimiter=',')
	for fn in names:
		num = '/'+fn[1]+'/'+fn[2]+'/'+fn[3]
		num1 = fn[3]
		num1 = num1.split('-')
		num1 = num1[1]
		with open('oai_last.csv') as oai:
			tit = csv.reader(oai, delimiter='|')
			for row in tit:
				if row[9] == num1:
					cr = row[0]
					cr = cr[:-2]
					cr = cr.split(',')
					name = cr[0]
					typ = row[7]
					if typ == "ABS":
						print (num)

