#!/usr/bin/env python

# Extracting Text from a PDF file
# Using the pdfminer library, extracts text directly PDF if PDF allows direct text extraction
# If this fails, indirectly uses Tesseract's OCR library to extract text

import os
import sys
import subprocess
from wand.image import Image
from PIL import Image as PI
from pytesseract import image_to_string
from PyPDF2 import PdfFileReader
from datetime import datetime

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO


def extract_Text_Directly(file_name):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'ascii'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    with open(file_name, 'rb') as fp:
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = ""
        maxpages = 0
        caching = True
        pagenos=set()

        for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
            interpreter.process_page(page)

        text = retstr.getvalue().strip()

        fp.close()
    device.close()
    retstr.close()
    return text


# text_data = extract_Text_Directly("/home/skluzacek/Desktop/skluma_paper_escience.pdf")

# print(text_data)