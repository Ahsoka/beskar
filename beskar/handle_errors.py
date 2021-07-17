from sentry_sdk.utils import event_from_exception
from PyQt6.QtCore import QCoreApplication
from .popups import ErrorPopup
from sentry_sdk import Hub
from . import window

import traceback
import pathlib
import inspect
import logging
import sys

def handle_exception(exc_type, exc_value, trace):
    try:
        exc_tuple = (exc_type, exc_value, trace)
        error_message = ''.join(traceback.format_exception(*exc_tuple))

        popup = ErrorPopup(window, error_message)
        popup.exec()

        if popup.sending:
            hub = Hub.current
            if hub.client is not None:
                hub.capture_event(*event_from_exception(exc_tuple))
                hub.flush()

        stack = inspect.stack()[1]
        module = inspect.getmodule(stack.frame)
        if module:
            module_name = module.__name__
        else:
            path = pathlib.Path(stack.filename)
            module_name = f"{path.parent.name}.{path.stem}"

        if module_name in sys.modules:
            logger = logging.getLogger(module_name)
        else:
            logger = logging.getLogger('beskar.unknown')
            logger.warning(
                'Failed to determine which module caused '
                'the error in the upcoming logging message.'
            )

        logger.critical('The following error occured:', exc_info=exc_tuple)

        QCoreApplication.quit()
    finally:
        sys.exit(1)
