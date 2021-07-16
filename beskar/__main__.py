from sentry_sdk.utils import event_from_exception
from .settings import logging_dir
from .popups import ErrorPopup
from .logs import setUpLogger
from sentry_sdk import Hub
from . import app, window

import sys
import logging
import inspect
import traceback

def handle_exception(exc_type, exc_value, trace):
    exc_tuple = (exc_type, exc_value, trace)
    error_message = ''.join(traceback.format_exception(*exc_tuple))

    popup = ErrorPopup(window, error_message)
    popup.exec()

    # Get logger for the file that is responsible for error
    logger = logging.getLogger(inspect.getmodule(inspect.stack()[1].frame).__name__)
    logger.critical('The following error occured:', exc_info=exc_tuple)

    if popup.sending:
        hub = Hub.current
        if hub.client is not None:
            hub.capture_event(*event_from_exception(exc_tuple))
            hub.flush()

    sys.exit(1)

def main():
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    for logger_name in map(
        lambda name: f'beskar.{name}',
        ('gui', 'pages', 'popups', 'settings', 'utils')
    ):
        setUpLogger(
            logger_name,
            '%(levelname)s | %(name)s: [%(funcName)s()] %(message)s',
            logging_dir
        )

    sys.excepthook = handle_exception
    main()
