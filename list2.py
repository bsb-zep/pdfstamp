import csv

with open('log_all_2.csv') as liste:
	names = csv.reader(liste, delimiter='/')
	for fn in names:
		num = '/'+fn[1]+'/'+fn[2]+'/'+fn[3]
		num1 = fn[3]
		num1 = num1.split('-')
		num1 = num1[1]
		with open('abs.csv') as abss:
			numm = '/'+fn[1]+'/'+fn[2]+'/'+fn[3]
			num2 = fn[3]
			num2 = num2.split('-')
			num2 = num2[1]
			for row in abss:
				if num1 == num2:
					if typ == "ABS":
						print (num)
					else:
						print (numm)

