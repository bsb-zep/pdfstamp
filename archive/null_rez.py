import PyPDF2 
import io 
import csv 
from lxml import etree
import subprocess

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm, inch
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle



with open('rez.csv') as kurz:
	namek = csv.reader(kurz, delimiter='/', quotechar='#')
	for fn in namek:
		try:
			num = '/'+fn[1]+'/'+fn[2]+'/'+fn[3]
			num1 = fn[3]
			num1 = num1.split('-')
			num1 = num1[1]
			subprocess.call(["identify -define pdf:use-cropbox=true -format \"%[pdf:HiResBoundingBox]\" /home/anovikov/articles"+num+"[0] > cropkoor.csv"], shell=True)
			subprocess.call(["python3 pdf2txt.py -p 1 -t xml /home/anovikov/articles"+num+" > koord.xml"], shell=True)
			with open('cropkoor.csv') as koor:
				cs = csv.reader(koor, delimiter='x')
				for row in cs:
					rez = row[1]
					rezGr = rez[:3]
					rezGr = rezGr.split('.')
					rezGr = int(rezGr[0])
					rez = rez.split('+')
					diff = rez[2]+'.'
					diff = diff.split('.')
					diff = diff[0]
					if row == 0:
						print (num)		
			Stempel = io.BytesIO()
			Blank =io.BytesIO()
			tree = etree.parse("koord.xml")
			root = tree.getroot()

			# Koordinaten bearbeitung
			for textbox in root.findall("./page[@id='1']/textbox[last()-1]/textline"):
				bottomTest = textbox.attrib['bbox']
				bottomTest = bottomTest.split(',')
				bottomTest = bottomTest[1].split('.')
				bottomTest = int(bottomTest[0])
			for textbox in root.findall("./page[@id='1']/textbox[last()0]/textline"):
				bottom = textbox.attrib['bbox']
				bottom = bottom.split(',')
				bottom = bottom[1].split('.')
				bottom = int(bottom[0])
				if bottom > bottomTest: # Ob es etwas unter der Seitenzahl gibt
					bottom = bottomTest
			# Ränder
			rand_list = ""
			for textbox in root.findall("./page/textbox/textline"):
				rechts = textbox.attrib['bbox']
				rechts = rechts.split(',')
				rechts = rechts[0].split('.')
				rechts = rechts[0]
				rand_list += rechts+' '
			rand_list = rand_list.split()
			rand_list = sorted(rand_list)
			rechts = int(min(rand_list, key=int))
			rand_list = ""
			for textbox in root.findall("./page/textbox/textline"):
				links = textbox.attrib['bbox']
				links = links.split(',')
				links = links[2].split('.')
				links = links[0]
				rand_list += links+' '
			rand_list = rand_list.split()
			rand_list = sorted(rand_list)
			links = int(max(rand_list, key=int))
			#print ("Links: ", links)

			for textbox in root.findall('./page[@id="1"]/textbox[@id="0"]/textline[last()1]'):
				top = textbox.attrib['bbox']
				top = top.split(',')
				top = top[1].split('.')
				top = int(top[0])

			for page in root.findall("page[@id='1']"):
				page = page.attrib['bbox']
				page = page.split(',')
				breite = page[2].split('.')
				breite = int(breite[0])
				page = page[3].split('.')
				page = int(page[0])

			# Stempelgröße bestimmen
			textBr = breite-(breite-links)-rechts-110
			testBr = textBr // 4.6
			#print ("TextBr: ", textBr, "\nKegel: ", testBr, "\nFile name: ", num)

			if testBr > 110:
				fontS = 12
				lead = 13
				#br = 103
				mn = 10 # Luft
			elif testBr > 90:
				fontS = 10
				lead = 11
				#br = 103
				mn = 8
			else:
				fontS = 8
				lead = 9
				#br = 103
				mn = 7

			pdfmetrics.registerFont(TTFont('Reg', 'reg.ttf'))
			pdfmetrics.registerFont(TTFont('Regi', 'regi.ttf'))
			addMapping('Reg', 0, 0, 'Reg')
			addMapping('Reg',0,1,'Regi')
			style = ParagraphStyle(
				name='Normal',
				fontName='Reg',
				fontSize=fontS,
				leading=lead,
				borderWidth=0,
				borderColor='Black',
				borderPadding=2,
			)
			xx = 0
			#xx2 = 0
			#xx3 = 0
			# with open('table.csv') as csvfile:
			#     csv = csv.reader(csvfile, delimiter='°', quotechar='|')
			#     #csvList= list(csv)
			#     for row in csv:
			#         csvL += row[0]+". "

			with open('oai_last.csv') as csvfile:
				csvv = csv.reader(csvfile, delimiter='|', quotechar='#')
				#csvList= list(csv)
				csvL = ""
				tt = ""
				for row in csvv:
					if row[9] == num1:
						cr = row[0]
						cr = cr[:-2]
						cr = cr.split(',')
						name = cr[0]
						vorname = cr[1]
						tit = row[1]
						bd = row[2]
						hf = row[3]
						jg = row[4]
						sz = row[5]
						doi = row[6]
						typ = row[7]
						if typ == 'REZ':
							reztit = tit.split(',')
							rez_name = reztit[0]
							rez_rest = reztit[1]
							tt = "<i>"+name+"</i>, "+vorname+": Rezension zu: <i>"+rez_name+"</i>, "+rez_rest+". In: Bohemia "+bd+" ("+jg+") H. "+hf+", "+sz+"."
							zz = 'zitierfähiger Link: <link href="'+doi+'">'+doi+'</link>'
							cc = "© Alle Rechte vorbehalten."
						#csvL = str(tt)
						elif typ == 'ART':
							tt = "<i>"+name+"</i>, "+vorname+": "+tit+". In: Bohemia "+bd+" ("+jg+") H. "+hf+", "+sz+"."
							zz = 'zitierfähiger Link: <link href="'+doi+'">'+doi+'</link>'
							cc = "© Alle Rechte vorbehalten."
						elif typ == 'ABS':
							zz = 'zitierfähiger Link: <link href="'+doi+'">'+doi+'</link>'
							cc = "© Alle Rechte vorbehalten."
							tt = "Abstract zu: "+ "<i>"+name+"</i>, "+vorname+": "+tit+". In: Bohemia "+bd+" ("+jg+") H. "+hf+"."
						else:
							zz = 'zitierfähiger Link: <link href="'+doi+'">'+doi+'</link>'
							cc = "© Alle Rechte vorbehalten." 
							tt = "<i>"+name+"</i>, "+vorname+": Tagungsbericht zu: "+tit+". In: Bohemia "+bd+" ("+jg+") H. "+hf+", "+sz+"."
				csvLen = len(str(tt))
				csvcount = csvLen// testBr+1
				#print ("Zeilen: ", csvcount)
				csvcount = csvLen// testBr + 4
				#test = csvLen//csvcount
				#print ("Px in einer Zeile: ", test) 
				#topfree = (page-mn) - top
				#bottempty = (bottom-15) // fontS
				#topempty = topfree // fontS
				zahl = csvcount*lead
		except IndexError:
			print ("Fehler: ", num)
			#print ("\n\nRow Info: ", row)
			continue
