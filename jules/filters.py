try:
    from html.parser import HTMLParser
except ImportError:
    from HTMLParser import HTMLParser
from xml.sax.saxutils import escape
import re

from bs4 import BeautifulSoup

try:
    string = unicode
except NameError:
    string = str


def register(func):
    globals()[func.__name__] = func

def iso8601(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

def firstCap(string):
    return string[:1].upper() + string[1:]

def smartTitle(string):
    parts = re.split('([\w\']+)', string)
    parts = [firstCap(p) for p in parts]
    return ''.join(parts)

def truncateHTML(html, length=140):
    return string(BeautifulSoup(html[:length], "html.parser"))

def escapeForXML(html):
    h = HTMLParser()
    html = h.unescape(html)
    return escape(html)
