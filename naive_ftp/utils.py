import inspect
import os


def caller() -> str:
    '''
    Return the caller function name.
    '''

    return inspect.stack()[2][3]


def log(level: str, msg: str) -> None:
    '''
    A simple logger.

    Log format: [LEVEL] caller: msg

    :param level: log level, can be 'debug' / 'info' / 'warn' / 'error' / 'fatal'
    :param msg: message body
    '''

    print(f'[{level.upper():5}] {caller()}: {msg}')


def is_safe_path(path: str, base_dir: str, allow_base: bool = False) -> bool:
    '''
    Check if the requested path is safe to access.

    Return True if the path is located in base_dir, else return False.

    :param path: requested path
    :param base_dir: base directory, requested path should be restricted inside
    :param allow_base: if allowed to access base directory
    '''

    if not allow_base:
        base_dir += os.sep
    return os.path.realpath(path).startswith(base_dir)