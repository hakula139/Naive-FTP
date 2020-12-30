def log(level: str, src: str, msg: str) -> None:
    '''
    A simple logger.

    Log format: [LEVEL] src: msg

    :param level: log level, can be 'debug' / 'info' / 'warn' / 'error' / 'fatal'
    :param src: caller function name
    :param msg: message body
    '''

    print(f'[{level.upper():5}] {src}: {msg}')


def is_safe_path(path: str, base_dir: str) -> bool:
    '''
    Check if the requested path is safe to access.

    Return True if the path is located in base_dir, else return False.

    :param path: requested path
    :param base_dir: base directory, requested path should be restricted inside
    '''

    return path.startswith(base_dir)
