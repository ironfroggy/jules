import re

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
