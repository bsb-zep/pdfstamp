import PyPDF2
import io
import csv
import os
from lxml import etree
import subprocess
import re
import sys
import traceback
import logging
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm, inch
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


class Document:

    def __init__(self, originName, metadata):
        # define logging properties
        self.logger = logging.getLogger(__name__)
        handler = logging.FileHandler('../log')
        handler.setLevel(logging.ERROR)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
		
        # common configuration
        self.metadata = metadata
        self.fileDir = '../../../articles/' + originName.split('-')[0] + '/public/'
        self.filePath = self.fileDir + originName
        self.fileName = originName
		
        self.backgroundFile = '../../white.png'
        self.logoFile = '../../logo.png'
        self.blankPdf = '../blank.pdf'
        self.outPdf = '../../../articles_stamped/' + originName.split('-')[0] + '/public/' + originName

        #  some stamp params
        self.logoWidth = 120
        self.logoHeight = 41
        self.paddingBottom = 10
        self.paddingTop = 5
        self.linespace = 3

    def startPdfParser(self):
        self.getPageCoors()
        if self.getOcrCoors():
            self.setDocType()
            self.parseMetadata()
            self.getStampSize()
            self.setStampPosition()
            self.setStampParams()
            self.createStampTpl()
            self.mergePDFs()
        else:
            self.logger.error('PDF coordinates are currupt or unreadable. Filename: '+self.filePath)
            next

    def getPageCoors(self):
        # check if pdfinfo installed
        progName = 'pdfinfo'
        status = subprocess.getstatusoutput(progName)[0]
        if status != 127:
            out_box = subprocess.check_output(
                [progName + " -box -f 1 -l 1 "+self.filePath+"| grep -E 'MediaBox|CropBox'"], shell=True)
            boxes = str(out_box)
            boxex = boxes.replace("   ", ",")
            boxes = boxex.replace(" ", "")
            boxes = boxes.split("\\n")

            # cropBox coordinates
            CropBox = boxes[1].split(",")
            #print(CropBox)
            self.cropBottom = int(float(CropBox[4]))
            self.cropX = int(float(CropBox[5]))
			
            self.cropY = int(float(CropBox[6]))

            # mediaBox coordinates
            MediaBox = boxes[0].split(",")
            self.mediaBottom = int(float(MediaBox[3]))
            self.mediaX = int(float(MediaBox[4]))
            self.mediaY = int(float(MediaBox[5]))
            #print(MediaBox)

        else:
            # self.logger.error(progName + ' not installed on your system.')
            print("Error: '" + progName + "' not installed on your system.")

    def getOcrCoors(self):
        try:
            # get OCR data
            proc = subprocess.Popen(['python', '../vendor/pdfminer/tools/pdf2txt.py',
                                     '-p', '1', '-t', 'xml', self.filePath], stdout=subprocess.PIPE)
            procOutput = proc.communicate()[0]
            tree = etree.fromstring(procOutput)
            root = tree.getroottree()
            # Parse OCR-Text coordinates
            # check if there is text on the right bottom side
            for textbox in root.findall("./page[@id='1']/textbox[last()-1]/textline[last()]"):
                bottomTest = textbox.attrib['bbox']
                bottomTest = bottomTest.split(',')
                bottomTest = bottomTest[1].split('.')
                textBottomRight = int(bottomTest[0])

            # get coors for the text on the bottom
            for textbox in root.findall("./page[@id='1']/textbox[last()]/textline[last()]"):
                bottom = textbox.attrib['bbox']
                bottom = bottom.split(',')
                bottom = bottom[1].split('.')
                self.textBottom = int(bottom[0])
                self.textBottom = textBottomRight if self.textBottom > textBottomRight else self.textBottom

            # Get OCR lmargins
            rand_list = ""
            for textbox in root.findall("./page/textbox/textline"):
                right = textbox.attrib['bbox']
                right = right.split(',')
                right = right[0].split('.')
                right = right[0]
                rand_list += right+' '
            rand_list = rand_list.split()
            rand_list = sorted(rand_list)
            self.textRight = int(min(rand_list, key=int))
            rand_list = ""

            for textbox in root.findall("./page/textbox/textline"):
                left = textbox.attrib['bbox']
                left = left.split(',')
                left = left[2].split('.')
                left = left[0]
                rand_list += left+' '
            rand_list = rand_list.split()
            rand_list = sorted(rand_list)
            self.textLeft = int(max(rand_list, key=int))

            for textbox in root.findall('./page[@id="1"]/textbox[@id="0"]/textline[last()1]'):
                top = textbox.attrib['bbox']
                top = top.split(',')
                top = top[1].split('.')
                self.textTop = int(top[0])

            for page in root.findall("page[@id='1']"):
                page = page.attrib['bbox']
                page = page.split(',')
                breite = page[2].split('.')
                self.breite = int(breite[0])
                page = page[3].split('.')
                self.pageWidth = int(page[0])

            self.stampAreaWidth = self.textLeft-self.textRight
            return True
        except Exception as e:
            self.logger.warning('Pdf coordinates are currupt or unreadable. Filename: '+self.filePath)
            self.logger.error(e)
            next
            return False

    def setDocType(self):
        try:
            self.backgroundWidth = self.mediaX
            self.logoX = self.textLeft - self.logoWidth
            self.textWidth = self.textLeft - self.textRight - self.logoWidth
            if self.cropY == self.mediaY and self.cropBottom == 0:
                self.mode = 'no crop'
                self.marginTop = self.mediaY - self.textTop
                self.marginBottom = self.textBottom
                self.bottomSpace = self.marginBottom
                self.topSpace = self.marginTop
            elif self.cropY != self.mediaY or self.cropBottom > 0:
                self.mode = 'croped'
                self.marginTop = self.mediaY - self.textTop
                self.marginBottom = self.cropBottom
                self.bottomSpace = self.marginBottom
                self.topSpace = self.mediaY - self.cropY
                
        except Exception as e:
            self.logger.warning(e)
            next

    def getStampSize(self):
        try:
            self.Stamp = io.BytesIO()
            self.tempSeite = canvas.Canvas(self.Stamp)
            style = self.setFontArt(self.stampText)

            self.textStampP = Paragraph(self.stampText, style)
            self.stampLinkP = Paragraph(self.stampLink, style)
            self.stampCopyP = Paragraph(self.stampCopy, style)

            #  get X/Y coors of the stamp on the temp page
            textStampW, self.textStampH = self.textStampP.wrapOn(
                self.tempSeite, self.textWidth, self.cropY)
            linkW, self.linkH = self.stampLinkP.wrapOn(
                self.tempSeite, self.textWidth, self.cropY)
            copyW, self.copyH = self.stampCopyP.wrapOn(
                self.tempSeite, self.textWidth, self.cropY)
            self.stampSize = self.textStampH + self.linkH + self.copyH + \
                self.linespace*2 + self.paddingBottom + self.paddingTop
        except Exception as e:
            self.logger.warning("Can't define the stamp size for current file: "+self.filePath)
            next

    # check free space on the top/bottom and return boolean (true for bottom, false for top, None for no space)
    def checkTopBottom(self):
        if self.stampSize < self.bottomSpace:
            return True
        elif self.stampSize < self.topSpace:
            return False
        elif self.stampSize > self.bottomSpace and self.stampSize > self.topSpace:
            return None

    def setStampPosition(self):
        flag = self.checkTopBottom()
        if self.mode == 'no crop':
            if flag is None:
                self.mode = 'no space'
            elif flag:
                self.mode = 'bottom'
            elif not flag:
                self.mode = 'top'

        else:
            if flag is None:
                self.mode = 'no space'
            elif flag:
                self.mode = 'cropbottom'
            elif not flag:
                self.mode = 'croptop'

    def setStampParams(self):
        self.logger.info('Current document name: %s  --- MediaBox: %s %s --- CropBox: %s %s --- Stamp mode: %s --- Stamp size: %s --- top space: %s --- bottom space: %s', self.filePath, self.mediaX, self.mediaY, self.cropX, self.cropY, self.mode, self.stampSize, self.topSpace, self.bottomSpace)
        if self.mode == 'bottom':
            self.cropT = self.cropY
            self.cropB = 0
            self.backgroundHeight = self.stampSize
            self.backgroundY = 0
            self.logoY = self.backgroundHeight - self.logoHeight
            self.textY = self.backgroundHeight - self.textStampH - self.paddingTop

        elif self.mode == 'top':
            self.cropT = self.cropY
            self.cropB = 0
            self.backgroundHeight = self.stampSize
            self.backgroundY = self.mediaY - self.stampSize
            self.logoY = self.mediaY - self.logoHeight
            self.textY = self.mediaY - self.paddingTop - self.textStampH

        elif self.mode == 'cropbottom':
            self.cropT = self.cropY
            self.cropB = self.marginBottom - self.stampSize
            self.backgroundHeight = self.stampSize
            self.backgroundY = self.marginBottom - self.stampSize
            self.logoY = self.marginBottom - self.logoHeight
            self.textY = self.marginBottom - self.textStampH - self.paddingTop

        elif self.mode == 'croptop':
            self.backgroundHeight = self.stampSize
            self.backgroundY = self.cropY
            self.cropT = self.cropY + self.backgroundHeight
            self.cropB = self.marginBottom
            self.logoY = self.cropY + self.stampSize - self.logoHeight
            self.textY = self.cropY + self.stampSize - self.textStampH - self.paddingTop

    def createStampTpl(self):
        #  draw background
        self.tempSeite.drawImage(
            self.backgroundFile, 0, self.backgroundY, self.backgroundWidth, self.backgroundHeight)
        # draw logo
        self.tempSeite.drawImage(self.logoFile, self.logoX,
                                 self.logoY, self.logoWidth, self.logoHeight, mask='auto')
        #  draw stamp text
        self.textStampP.drawOn(self.tempSeite, self.textRight, self.textY)
        self.stampLinkP.drawOn(
            self.tempSeite, self.textRight, self.textY - self.linkH - self.linespace)
        self.stampCopyP.drawOn(
            self.tempSeite, self.textRight, self.textY - self.linkH - self.copyH - self.linespace*2)

        self.tempSeite.showPage()
        self.tempSeite.save()

    def mergePDFs(self):
        try:
            filee = self.filePath
            # get
            c = canvas.Canvas(self.blankPdf)
            c.setPageSize((self.breite, self.mediaY))
            c.showPage()
            c.save()
            urpdf = open(filee, 'rb')
            pdfReader = PyPDF2.PdfFileReader(urpdf)
            ersteSeite = pdfReader.getPage(0)
            pdfDReader = PyPDF2.PdfFileReader(self.blankPdf, 'rb')
            ersteSeite.mergeScaledPage(pdfDReader.getPage(0), 1)
            # crop from the bottom
            ersteSeite.cropBox.lowerLeft = (0, self.cropB)
            # crop from the top
            ersteSeite.cropBox.upperLeft = (0, self.cropT)
            pdfSReader = PyPDF2.PdfFileReader(self.Stamp)
            ersteSeite.mergeScaledPage(pdfSReader.getPage(0), 1)
            pdfWriter = PyPDF2.PdfFileWriter()
            pdfWriter.addPage(ersteSeite)
            pdfReader = PyPDF2.PdfFileReader(urpdf)
            for pageNum in range(1, pdfReader.numPages):
                pageObj = pdfReader.getPage(pageNum)
                pdfWriter.addPage(pageObj)

            endFile = open(self.outPdf, 'wb')
            pdfWriter.write(endFile)
            urpdf.close()
            endFile.close()
        except Exception as e:
            self.logger.error(e)
            next

    def getStampContent(self, row):
        try:
            self.stampCopy = '© Alle Rechte vorbehalten.'
            self.stampText = ''
            self.stampLink = ''

            creatorFullName = row[0][:-2].split(',')
            creatorLastName = creatorFullName[0]
            creatorFirstName = creatorFullName[1]
            title = row[1]
            vol = row[2]
            issue = row[3]
            year = row[4]
            pages = row[5]
            doi = row[6]
            category = row[7]

            if category == 'REZ':
                self.stampText = '<i>'+creatorLastName+'</i>, '+creatorFirstName+': Rezension zu: ' + \
                    title+'. In: Bohemia '+vol + \
                    ' ('+year+') H. '+issue+', '+pages+'.'
                self.stampLink = 'zitierfähiger Link: <link href="'+doi+'">'+doi+'</link>'
            elif category == 'ART':
                self.stampText = '<i>'+creatorLastName+'</i>, '+creatorFirstName+': '+title + \
                    '. In: Bohemia '+vol+' ('+year+') H. '+issue+', '+pages+'.'
                self.stampLink = 'zitierfähiger Link: <link href="'+doi+'">'+doi+'</link>'
            elif category == 'ABS':
                self.stampLink = 'zitierfähiger Link: <link href="'+doi+'">'+doi+'</link>'

                self.stampText = 'Abstract zu: ' + '<i>'+creatorLastName+'</i>, '+creatorFirstName + \
                    ': '+title+'. In: Bohemia '+vol+' ('+year+') H. '+issue+'.'
            else:
                self.stampLink = 'zitierfähiger Link: <link href="'+doi+'">'+doi+'</link>'
                self.stampText = '<i>'+creatorLastName+'</i>, '+creatorFirstName+': Tagungsbericht zu: ' + \
                    title+'. In: Bohemia '+vol + \
                    ' ('+year+') H. '+issue+', '+pages+'.'
            
            if self.stampText == '':
                self.logger.warning('Metadata for the current file is not found: '+self.filePath)
        except Exception as e:
            self.logger.warning('There is a Problem with metadata in the file: '+self.filePath)
            self.logger.error(e)
            next

    def parseMetadata(self):
        try:
            fileId = self.fileName.split('-')[1]

            with open(self.metadata) as csvfile:
                dataReader = csv.reader(csvfile, delimiter='|', quotechar='#')
                for row in dataReader:
                    if row[9] == fileId:
                        self.getStampContent(row)
        except Exception as e:
            self.logger.error(e)
            print(e)
            sys.exit()

    def setFontArt(self, t):
        try:
            tt = t
            fontS = 8
            lead = 9
            pdfmetrics.registerFont(TTFont('Reg', '../vendor/reg.ttf'))
            pdfmetrics.registerFont(TTFont('Regi', '../vendor/regi.ttf'))
            addMapping('Reg', 0, 0, 'Reg')
            addMapping('Reg', 0, 1, 'Regi')
            style1 = ParagraphStyle(
                name='Normal',
                fontName='Reg',
                fontSize=fontS,
                leading=lead,
                borderWidth=0,
                borderColor='Black',
                borderPadding=0,
                wordWrap='LTR'
            )

            pdfmetrics.registerFont(TTFont('Free', '../vendor/FreeSerif.ttf'))
            pdfmetrics.registerFont(
                TTFont('FreeIt', '../vendor/FreeSerifItalic.ttf'))
            addMapping('Free', 0, 0, 'Free')
            addMapping('Free', 0, 1, 'FreeIt')
            style2 = ParagraphStyle(
                name='Normal',
                fontName='Free',
                fontSize=fontS,
                leading=lead,
                borderWidth=0,
                borderColor='Black',
                borderPadding=2,
                wordWrap='LTR'
            )
            tt = re.sub("â", "-", tt)

            with open("../vendor/whitelist_reg.csv") as wlist:
                wl = csv.reader(wlist)
                wl = list(wl)
                white_reg = []
                for n in wl:
                    white_reg.append(n[0])

            with open("../vendor/whitelist_freeserif.csv") as wtlist:
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
                        self.logger.error("Achtung! Das folgende Symbol soll manuel überprüft werden: " + numm)
                        self.logger.error("Die entsprechende Datei liegt unter "+self.fileName)
            style = style2 if flag == 1 else style1
            return style
        except:
            self.logger.warning('')
            next
