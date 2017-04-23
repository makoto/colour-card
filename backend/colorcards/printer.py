import cStringIO
from io import BytesIO
import logging
import os
from PIL import Image
import pystache
from reportlab.pdfgen import canvas
from reportlab.lib import units, colors
from reportlab.lib.utils import ImageReader
import requests
import qrencode


CARD_WIDTH = 54 * units.mm
CARD_HEIGHT = 85 * units.mm


class CardPrinter(object):
    FORMATTERS = {}

    @classmethod
    def formatter(cls, fun):
        cls.FORMATTERS[fun.__name__] = fun
        return fun

    def __init__(self, format):
        self.format = format

    def generate(self, context):
        data = cStringIO.StringIO()
        c = canvas.Canvas(data, pagesize=(CARD_WIDTH, CARD_HEIGHT))

        for page in self.format:
            c.rotate(90)
            for element in page['card']:
                self.FORMATTERS[element['type']](c, element, context)

            c.showPage()

        c.save()
        return data.getvalue()


@CardPrinter.formatter
def QR(c, element, context):
    eclevel = {
        'L': qrencode.QR_ECLEVEL_L,
        'M': qrencode.QR_ECLEVEL_M,
        'Q': qrencode.QR_ECLEVEL_Q,
        'H': qrencode.QR_ECLEVEL_H
    }[element.get('eclevel', 'L')]

    version, pixels, qr = qrencode.encode(
        pystache.render(element['text'], context),
        0,
        eclevel,
        qrencode.QR_MODE_8,
        element.get('caseSensitive', True))
    qr = qr.resize((pixels * 64, pixels * 64), Image.NEAREST)
    size = element['size'] * units.mm
    c.drawImage(
        ImageReader(qr),
        float(element['x']) * units.mm,
        -float(element['y']) * units.mm - size,
        size, 
        size)


def drawText(c, element, x, y, align, data):
    font = element.get('font', 'Courier')
    size = int(element.get('size', 12))
    if align == 'right':
        x -= c.stringWidth(data, font, size)
    text = c.beginText()
    text.setTextOrigin(x, y)
    text.setFont(font, size)
    text.setLeading(float(element.get('leading', 12)))
    text.textLine(data)
    c.setFillColorRGB(*colors.HexColor(element.get('color', '#000000')).rgb())
    c.drawText(text)


@CardPrinter.formatter
def text(c, element, context):
    drawText(
        c,
        element,
        float(element['x']) * units.mm,
        -float(element['y']) * units.mm,
        element.get('align', 'left'),
        pystache.render(element['text'], context))


@CardPrinter.formatter
def textArray(c, element, context):
    data = pystache.render(element['text'], context).split(element['split'])
    cols = int(element['columns'])
    startX = float(element['x']) * units.mm
    startY = -float(element['y']) * units.mm
    colspacing = float(element['columnSpacing']) * units.mm
    rowspacing = -float(element['rowSpacing']) * units.mm

    for i in range(len(data)):
        drawText(c, element, startX + colspacing * (i % cols), startY + rowspacing * (i / cols), 'left', data[i])


@CardPrinter.formatter
def image(c, element, context):
    uri = pystache.render(element['uri'], context)
    if uri.startswith('http:') or uri.startswith('https:'):
        response = requests.get(uri)
        img = Image.open(BytesIO(response.content))
    else:    
        path = os.path.join(os.path.dirname(__file__), uri)
        img = Image.open(path)
    c.drawImage(
        ImageReader(img),
        element['x'] * units.mm,
        (-element['y'] - element['height']) * units.mm,
        element['width'] * units.mm,
        element['height'] * units.mm)
