def register(func):
    print "REGISTER", func.__name__
    globals()[func.__name__] = func

def iso8601(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
