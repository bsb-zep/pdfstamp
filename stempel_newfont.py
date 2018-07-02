import PyPDF2 
import io 
import csv 
from lxml import etree
import subprocess
from langdetect import detect
import os, sys
import re

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm, inch
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

with open('kurz_test.csv') as kurz:
	namek = csv.reader(kurz, delimiter=',', quotechar='#')
	for fn in namek:
		try:
			num = '/'+fn[1]+'/'+fn[2]+'/'+fn[3]
			num1 = fn[3]
			num1 = num1.split('-')
			num1 = num1[1]
			subprocess.call(["python3 pdf2txt.py -p 1 -t xml /home/anovikov/articles"+num+" > koord.xml"], shell=True)

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
			style1 = ParagraphStyle(
				name='Normal',
				fontName='Reg',
				fontSize=fontS,
				leading=lead,
				borderWidth=0,
				borderColor='Black',
				borderPadding=2,
			)

			pdfmetrics.registerFont(TTFont('Free', 'FreeSerif.ttf'))
			pdfmetrics.registerFont(TTFont('FreeIt', 'FreeSerifItalic.ttf'))
			addMapping('Free', 0, 0, 'Free')
			addMapping('Free',0,1,'FreeIt')
			style2 = ParagraphStyle(
				name='Normal',
				fontName='Free',
				fontSize=fontS,
				leading=lead,
				borderWidth=0,
				borderColor='Black',
				borderPadding=2,
			)
			
			xx = 0
			with open('oai_last.csv') as csvfile:
				csvv = csv.reader(csvfile, delimiter='|', quotechar='#')
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
							reztit = tit.split(':')
							rez_name = reztit[0]
							rez_rest = reztit[1]
							tt = "<i>"+name+"</i>, "+vorname+": Rezension zu: <i>"+rez_name+"</i>, "+rez_rest+". In: Bohemia "+bd+" ("+jg+") H. "+hf+", "+sz+"."
							zz = 'zitierfähiger Link: <link href="'+doi+'">'+doi+'</link>'
							print (tt)
							cc = "© Alle Rechte vorbehalten."
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
				csvcount = csvLen// testBr + 4
				topfree = (page-mn) - top
				bottempty = (bottom-15) // fontS
				topempty = topfree // fontS

				if bottom >= csvcount*lead:
					if csvcount > 1:
						xx = bottom+21 - (csvcount)*mn
						bild = bottom - 34
						bb = ((bottom-mn) - csvcount*mn)//2
						bild = bild-bb
						xx = xx - bb
						xx2 = xx -15
						xx3 = xx2 - 15
					else:
						xx = bottom-mn
						bild = xx
						xx2 = xx - 15
						xx3 = xx2 - 15
				elif bottom < csvcount*lead:
					if topfree >= csvcount*lead:
						xx = (page+22-(mn*csvcount))
						bild = page - 30
						xx2 = xx - 15
						xx3 = xx2 - 15
					elif topfree < csvcount*lead:
						csvL=""
						bild = 2000
						print ("Fehler! Es gibt keinen Platz für den Stempel.")
						print ("File: ", num)

				tempSeite = canvas.Canvas(Stempel)
				styles = getSampleStyleSheet()
				styleN = styles['Normal']
				# Teil 1
				tt = re.sub("‐", "-",tt)
				with open("whitelist_reg.csv") as wlist:
					wl = csv.reader(wlist)
					wl = list(wl)
					white_reg = []
					for n in wl:
						white_reg.append(n[0])
				with open("whitelist_freeserif.csv") as wtlist:
					wtl = csv.reader(wtlist)
					wtl = list(wtl)
					white_freeserif = []
					for x in wtl:
						white_freeserif.append(x[0])
				tt_list = list(tt)
				flag = 0
				for numm in tt_list:
					char = ord(numm)
					char = str(char)
					if char not in white_reg:
						flag = 1
						if char not in white_freeserif:
							print ("Achtung! Das folgende Symbol soll manuel überprüft werden: "+ numm)
							print ("Die entsprechende Datei liegt unter "+num)
				if flag == 1:
					style = style2
				else:
					style = style1
				print (flag)	
				#if detect(tt) == "el" or "ar":
				#	style = style2
				#elif "\u271d"  in tt:
				#	style = style2
				#else:
				#	style = style1
				textStempel = Paragraph(tt, style)
				#tempSeite.setFont('Reg', xx)
				#tempSeite.drawString(40, 50, doi)
				textStempel.wrapOn(tempSeite, textBr, xx)
				textStempel.drawOn(tempSeite, rechts, xx)
				# Teil 2
				textStempel = Paragraph(zz, style)
				#textStempel.wrapOn(tempSeite, textBr, 100)
				textStempel.wrapOn(tempSeite, textBr-10, xx2)
				textStempel.drawOn(tempSeite, rechts, xx2)
				# Teil 3
				textStempel = Paragraph(cc, style)
				textStempel.wrapOn(tempSeite, textBr, xx3)
				textStempel.drawOn(tempSeite, rechts, xx3)
				tempSeite.drawImage('logo.png', links-110, bild, 110, 37, mask='auto')
				tempSeite.showPage() 
				tempSeite.save()
				filee = "/home/anovikov/articles"+num
				# Merge zwei PDFs
				urpdf = open(filee, 'rb')
				pdfReader = PyPDF2.PdfFileReader(urpdf)
				ersteSeite = pdfReader.getPage(0)
				pdfStempelReader = PyPDF2.PdfFileReader(Stempel)
				ersteSeite.mergeScaledPage(pdfStempelReader.getPage(0),1)
				pdfWriter = PyPDF2.PdfFileWriter()
				pdfWriter.addPage(ersteSeite)
				for pageNum in range(1, pdfReader.numPages):
					   pageObj = pdfReader.getPage(pageNum)
					   pdfWriter.addPage(pageObj)
				ennd = "/home/anovikov/articles_stempel/articles"+num
				endFile = open(ennd, 'wb')
				pdfWriter.write(endFile)
				urpdf.close()
				endFile.close()
		except IndexError as errlog:
			print ("Fehler: ", num)
			print (errlog)
			#print ("\n\nRow Info: ", row)
			continue
