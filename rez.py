import PyPDF2 
import io 
import csv 
from lxml import etree
import subprocess
import re
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm, inch
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class originalPDF:

	def __init__(self, num):
		filedir = "/home/anovikov/articles"
		# read PDF coordinates
		out_box = subprocess.check_output(["pdfinfo -box -f 1 -l 1 "+filedir+num+"| grep -E 'MediaBox|CropBox'"],shell=True)
		boxes = str(out_box)
		boxex = boxes.replace("   ",",")
		boxes = boxex.replace(" ","")
		boxes = boxes.split("\\n")
		# get CropBox coordinates
		CropBox = boxes[1].split(",")
		CropBottom = int(float(CropBox[4]))
		CropRight = int(float(CropBox[5]))
		CropTop = int(float(CropBox[6]))
		# get MediaBox coordinates
		MediaBox = boxes[0].split(",")
		MediaBottom = int(float(MediaBox[3]))
		MediaRight = int(float(MediaBox[4]))
		MediaTop = int(float(MediaBox[5]))
		#get OCR data
		subprocess.call(["python3 pdf2txt.py -p 1 -t xml "+filedir+num+" > koord.xml"], shell=True)
		
		tree = etree.parse("koord.xml")
		root = tree.getroot()

		# Parse OCR-Text coordinates
		for textbox in root.findall("./page[@id='1']/textbox[last()-1]/textline"):
			bottomTest = textbox.attrib['bbox']
			bottomTest = bottomTest.split(',')
			bottomTest = bottomTest[1].split('.')
			bottomTest = int(bottomTest[0])
		for textbox in root.findall("./page[@id='1']/textbox[last()0]/textline"):
			bottom = textbox.attrib['bbox']
			bottom = bottom.split(',')
			bottom = bottom[1].split('.')
			bottom = int(bottom[0]) - 10
			if bottom > bottomTest: # Ob es etwas unter der Seitenzahl gibt
				bottom = bottomTest - 10
		# Get OCR margins
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
		# Stamp width
		stampareaWd = breite-(breite-links)-rechts-110
		self.CropBottom = CropBottom
		self.CropRight = CropRight
		self.CropTop = CropTop
		self.MediaBottom = MediaBottom
		self.MediaRight = MediaRight
		self.MediaTop = MediaTop
		self.stampareaWd = stampareaWd
		self.bottom = bottom
		self.top = top
		self.rechts = rechts
		self.breite = breite
		self.links = links
		#return CropBottom, CropRight, CropTop, MediaBottom, MediaRight, MediaTop, stampareaWd, bottom, top, rechts, breite, links

	def CropType(self,CropBottom, CropTop, MediaBottom, MediaTop, bottom, top, StampSize, firstBlockSize):
		stamp = StampSize
		zahl = firstBlockSize
		if CropTop == MediaTop:
			if CropBottom == MediaBottom:
				cropB = MediaBottom
				cropT = MediaTop
				if stamp < bottom-10:
					xx = bottom-zahl
					background = bottom-110
					image = bottom-37
					#print ("no CropBox. Unten.", num)
				elif stamp < MediaTop-top:
					xx = MediaTop - zahl - 10
					background = "NULL"
					image = MediaTop - 37 - 7
					#print ("no CropBox. Oben.", num)
				else:
					image = 0
					background = "NOSPACE"
					xx = 0
					print ("no space,", num)
			else:
				cropB = CropBottom - stamp
				cropT = MediaTop
				xx = CropBottom - zahl
				image = CropBottom - 37
				background = CropBottom - 110
				#print ("nur unten", num)
		else:
			if CropBottom == MediaBottom:
				cropB = 0
				if stamp < bottom:
					cropT = CropTop
					xx = bottom - zahl
					background = bottom - 110
					image = bottom - 37
					#print ("unten", num)
				else:
					cropT = CropTop + stamp + 15
					xx = cropT -  zahl - 10
					background = CropTop
					image = cropT - 37 - 7
					#print ("oben", image, xx, num)
				#print (bottom, stamp)
			else:
				if stamp < CropBottom:
					cropB = CropBottom - stamp - 15
					cropT = CropTop
					xx = CropBottom - zahl
					background = CropBottom - 110
					image = CropBottom - 37
					#print ("oben und unten. Unten gestempelt", num)

				else:
					cropB = CropBottom
					cropT = CropTop + stamp
					xx = cropT - zahl
					background = CropTop
					image = cropT - 37
					#print ("oben und unten. Oben gestempelt", stamp, image, xx, num)
		return cropB, cropT, xx, image, background


class Stamp:
	
	def setFontSize(self,width):
		#testWd = width // param

		if f.CropRight < 404:
			fontS = 8
			lead = 9
			#br = 103
			mn = 13 # Luft
		else:
			fontS = 8
			lead = 9
			#br = 103
			mn = 13
		return fontS, lead, mn


	def getStampText(self,num):
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
						tt = "<i>"+name+"</i>, "+vorname+": Rezension zu: "+tit+". In: Bohemia "+bd+" ("+jg+") H. "+hf+", "+sz+"."
						zz = 'zitierfähiger Link: <link href="'+doi+'">'+doi+'</link>'
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
			return tt, cc, zz
	def setFontArt(self,t):
		tt = t
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
		tt = re.sub("â", "-",tt)
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
			fontart = "Free"
		else:
			style = style1
			fontart = "Reg"
		return style
	def getStampSize(self,width, metadata):
		param = 4.6
		mn = 8
		testWd = width // param
		csvLen = len(str(metadata))
		firstBlock = csvLen// testWd
		wholeStamp = csvLen// testWd + 4
		firstBlockSize = int(float(firstBlock*mn))
		StampSize = int(float(wholeStamp*mn))
		return StampSize, firstBlockSize

	def toStamp(self,stampareaWd, cropB, cropT, xx, image, background, rechts, tt, cc, zz, breite, MediaTop, links):
		logoW = 110
		logoH = 37
		backW = 500
		backH = 110
		Stempel = io.BytesIO()
		Blank =io.BytesIO()
		tempSeite = canvas.Canvas(Stempel)
		#styles = getSampleStyleSheet()
		#styleN = styles['Normal']
		style = s.setFontArt(tt)
		if background != "NOSPACE":
			if background != "NULL": tempSeite.drawImage('white.png', 0, background, backW, backH)
			textStempel = Paragraph(tt, style = style)
			textStempel.wrapOn(tempSeite, stampareaWd, 100)
			textStempel.drawOn(tempSeite, rechts, xx)
			textStempel = Paragraph(zz, style = style)
			textStempel.wrapOn(tempSeite, stampareaWd, 100)
			textStempel.drawOn(tempSeite, rechts, xx-15)
			textStempel = Paragraph(cc, style = style)
			textStempel.wrapOn(tempSeite, stampareaWd, 100)
			textStempel.drawOn(tempSeite, rechts, xx-30)
			tempSeite.drawImage('logo.png', links-110, image, logoW, logoH, mask='auto')
		tempSeite.showPage()
		tempSeite.save()
		#cropPx = cropST
		filee = "/home/anovikov/articles"+num
		# Merge zwei PDFs
		c = canvas.Canvas('blank.pdf')
		c.setPageSize((breite,MediaTop))
		c.showPage()
		c.save()
		urpdf = open(filee, 'rb')
		pdfReader = PyPDF2.PdfFileReader(urpdf)
		ersteSeite = pdfReader.getPage(0)
		pdfDReader = PyPDF2.PdfFileReader('blank.pdf', 'rb')
		ersteSeite.mergeScaledPage(pdfDReader.getPage(0),1)
		ersteSeite.cropBox.lowerLeft = (0,cropB)
		ersteSeite.cropBox.upperLeft = (0,cropT)
		pdfSReader = PyPDF2.PdfFileReader(Stempel)
		ersteSeite.mergeScaledPage(pdfSReader.getPage(0),1)
		pdfWriter = PyPDF2.PdfFileWriter()
		pdfWriter.addPage(ersteSeite)
		pdfReader = PyPDF2.PdfFileReader(urpdf)
		for pageNum in range(1, pdfReader.numPages):
			pageObj = pdfReader.getPage(pageNum)
			pdfWriter.addPage(pageObj)
		ennd = "/home/anovikov/articles_stempel/articles"+num
		endFile = open(ennd, 'wb')
		pdfWriter.write(endFile)
		urpdf.close()
		endFile.close()


with open('kurz_test.csv') as kurz:
	namek = csv.reader(kurz, delimiter=',', quotechar='#')
	for fn in namek:
		try:
			num = '/'+fn[1]+'/'+fn[2]+'/'+fn[3]
			num1 = fn[3]
			num1 = num1.split('-')
			num1 = num1[1]
			f = originalPDF(num)
			s = Stamp()
			tt, cc, zz = s.getStampText(num1)
			StampSize, firstBlockSize = s.getStampSize(f.stampareaWd, tt)
			fontS, lead, mn = s.setFontSize(f.stampareaWd)
			#style = s.setFontArt(tt)
			cropB, cropT, xx, image, background = f.CropType(f.CropBottom, f.CropTop, f.MediaBottom, f.MediaTop, f.bottom, f.top, StampSize, firstBlockSize)
			test = s.toStamp(f.stampareaWd, cropB, cropT, xx, image, background, f.rechts, tt, cc, zz, f.breite, f.MediaTop, f.links)	
		except IndexError:
			print ("Error,", num)
			continue
