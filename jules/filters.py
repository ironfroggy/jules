def register(func):
    print "REGISTER", func.__name__
    globals()[func.__name__] = func
