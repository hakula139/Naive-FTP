import inspect
import os
from datetime import date, datetime


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

    log_msg = f'[{level.upper():5}] {caller()}: {msg}'
    print(log_msg)


def logf(level: str, msg: str) -> None:
    '''
    An alias for the logger, which writes to a file.

    Log format: time - [LEVEL] caller: msg

    :param level: log level, can be 'debug' / 'info' / 'warn' / 'error' / 'fatal'
    :param msg: message body
    '''

    current_date = date.today().strftime('%Y-%m-%d')
    current_time = datetime.now().strftime('%H:%M:%S')

    log_dir = os.path.realpath('logs')
    log_name = f'{current_date}.log'
    log_path = os.path.join(log_dir, log_name)
    log_msg = f'{current_time} - [{level.upper():5}] {caller()}: {msg}\n'

    try:
        with open(log_path, 'a') as log_file:
            log_file.write(log_msg)
    except OSError as e:
        log('error', f'Failed to write to a log file, error: {e}')


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
