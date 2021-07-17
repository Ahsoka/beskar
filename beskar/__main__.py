from .handle_errors import handle_exception
from .settings import logging_dir
from .logs import setUpLogger
from . import app, window

import sys

def main():
    for logger_name in map(
        lambda name: f'beskar.{name}',
        ('gui', 'pages', 'popups', 'settings', 'utils', 'unknown')
    ):
        setUpLogger(logger_name, logging_dir)

    sys.excepthook = handle_exception

    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
