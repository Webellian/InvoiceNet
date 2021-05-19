# Copyright (c) 2019 Tradeshift
# Copyright (c) 2020 Sarthak Mittal
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re
import io
import math
import datetime
import datefinder
import pytesseract
from pytesseract import Output
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTTextLine, LTChar, LTAnno

class TextParser:

    def __init__(self):
        self.template = dict()
        self.template['amount'] = [r'\d+[,\d]*\.\d+']
        self.template['date'] = [r'\d{1,2}[\/\\\.\,-]\d{1,2}[\/\\\.\,-]\d{2,4}',
                                 r'\d{2,4}[\/\\\.\,-]\d{1,2}[\/\\\.\,-]\d{1,2}']

    def parse(self, text, key):
        if key == 'date':
            try:
                matches = [date for date in datefinder.find_dates(text) if date <= datetime.datetime.today()]
                if matches:
                    return True
                else:
                    return False
            except Exception:
                return False
        if key not in self.template:
            return False
        for regex in self.template[key]:
            if re.findall(regex, text):
                return True
        return False

    def find(self, text, key):
        if key == 'date':
            try:
                matches = [date for date in datefinder.find_dates(text) if date <= datetime.datetime.today()]
                if len(matches) > 0:
                    return [match.strftime('%m-%d-%Y') for match in matches]
                else:
                    return []
            except Exception:
                return []
        values = []
        if key not in self.template:
            return values
        for regex in self.template[key]:
            values.extend(re.findall(regex, text))
        values = list(set(values))
        return values

    def replace(self, text, new, key):
        if key not in self.template:
            return text
        for regex in self.template[key]:
            text = re.sub(regex, new, text)
        while '  ' in text:
            text = text.replace('  ', ' ')
        return text


def pdfminer_extract_words(line, page_height):
    def dpi_scaling(value):
        pdf2image_default_dpi = 200
        pdfminer_default_dpi = 72
        return int(value * pdf2image_default_dpi / pdfminer_default_dpi)

    words = []
    word = LTTextContainer()
    for char in line:
        if isinstance(char, LTAnno) or char.get_text() == ' ':
            if word.get_text():
                words.append(word)
            word = LTTextContainer()
        else:
            assert isinstance(char, LTChar)
            word.add(char)
    assert len(word) == 0

    scaled_words = [
        {
            'text': word.get_text(),
            'left': dpi_scaling(word.x0),
            'top': dpi_scaling(page_height - word.y1),
            'right': dpi_scaling(word.x1),
            'bottom': dpi_scaling(page_height - word.y0)
        }
        for word in words
    ]
    return scaled_words

def pdfminer_extract_lines(path):
    for page_layout in extract_pages(path):
        lines = []
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    if isinstance(text_line, LTTextLine):
                        lines.append(pdfminer_extract_words(text_line, page_layout.height))
    return lines

def extract_words_using_ocr(img, height, width, ocr_engine=None):
    if ocr_engine == None:
        ocr_engine = 'pytesseract'
    if ocr_engine == 'pytesseract':
        data = pytesseract.image_to_data(img, output_type=Output.DICT)
        n_boxes = len(data['text'])
        words = [
            {
                'text': data['text'][i],
                'left': data['left'][i],
                'top': data['top'][i],
                'right': data['left'][i] + data['width'][i],
                'bottom': data['top'][i] + data['height'][i]
            }
            for i in range(n_boxes) if data['text'][i]
        ]
        return words

    elif ocr_engine == 'aws_textract':

        import boto3

        # use aws textract
        client = boto3.client('textract')

        # convert PpmImageFile to byte
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        # call aws-textract API
        response = client.detect_document_text(Document={'Bytes': img_byte_arr})

        # get image weight and height to convert normalized coordinate from response
        words = [
            {
                'text': data['Text'],
                'left': math.floor((data['Geometry']['BoundingBox']['Left']) * width),
                'top': math.floor((data['Geometry']['BoundingBox']['Top']) * height),
                'right': math.ceil(
                    (data['Geometry']['BoundingBox']['Left'] + data['Geometry']['BoundingBox']['Width']) * width),
                'bottom': math.ceil(
                    (data['Geometry']['BoundingBox']['Top'] + data['Geometry']['BoundingBox']['Height']) * height)
            } for data in response['Blocks'] if "Text" in data
        ]
        return words


def divide_into_lines(words, height, width):
    cur = words[0]
    lines = []
    line = []
    for word in words:
        if ((word['top'] - cur['top']) / height) > 0.005:
            # if difference between y-coordinate of current word and previous word
            # is more than 0.5% of the height, consider the current word to be in the next line
            lines.append(line)
            line = [word]
        elif ((word['left'] - cur['right']) / width) > 0.05:
            # if difference between x-coordinate of current word and previous word
            # is more than 5% of the width, consider the current word to be in a different line
            lines.append(line)
            line = [word]
        else:
            line.append(word)
        cur = word
    lines.append(line)
    return lines


def create_ngrams(path, img, height, width, length=4, ocr_engine=None):
    if ocr_engine == 'pdfminer' or ocr_engine == None:
        lines = pdfminer_extract_lines(path)
    else:
        words = extract_words_using_ocr(img, height=height, width=width, ocr_engine=ocr_engine)
        lines = divide_into_lines(words, height=img.size[1], width=img.size[0])
    tokens = [line[i:i + N] for line in lines for N in range(1, length + 1) for i in range(len(line) - N + 1)]
    ngrams = []
    parser = TextParser()

    for token in tokens:
        text = ' '.join([word['text'] for word in token])
        ngram = {
            "words": token,
            "parses": {}
        }
        if parser.parse(text=text, key='date'):
            ngram["parses"]["date"] = parser.find(text=text, key='date')[0]
        elif parser.parse(text=text, key='amount'):
            ngram["parses"]["amount"] = parser.find(text=text, key='amount')[0]
        ngrams.append(ngram)

    return ngrams


def normalize(text, key):
    if key == 'amount':
        text = text.replace(",", '')
        splits = text.split('.')
        if len(splits) == 1:
            text += ".00"
        else:
            text = splits[0] + '.' + splits[1][:2]
    else:
        matches = [date for date in datefinder.find_dates(text) if date <= datetime.datetime.today()]
        if matches:
            text = matches[0].strftime('%m-%d-%Y')
    return text
