def log(level: str, src: str, msg: str) -> None:
    '''
    A simple logger.

    Log format: [LEVEL] src: msg

    :param level: log level, can be 'debug' / 'info' / 'warn' / 'error' / 'fatal'
    :param src: caller function name
    :param msg: message body
    '''

    print(f'[{level.upper():5}] {src}: {msg}')
