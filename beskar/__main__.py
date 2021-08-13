from . import app, startup, update_thread
from .settings import logging_dir
from .gui import BeskarWindow
from .logs import setUpLogger

import sys

def main():
    for logger_name in map(
        lambda name: f'beskar.{name}',
        ('gui', 'utils', 'unknown', 'update')
    ):
        setUpLogger(logger_name, logging_dir)

    if update_thread:
        update_thread.start()

    startup.show()

    if startup.exec():
        window = BeskarWindow(startup.mocked, startup.device_name)
        window.show()
        sys.exit(app.exec())

if __name__ == '__main__':
    main()
