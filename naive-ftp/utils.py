def log(level, src, msg):
    '''
    A simple logger
        level: debug / info / warn / error / fatal
        src:   called by which function
        msg:   log message
    '''

    print(f'[{level.upper():5}] {src}: {msg}')
