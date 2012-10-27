def register(func):
    globals()[func.__name__] = func
