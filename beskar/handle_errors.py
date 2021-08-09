from sentry_sdk.utils import event_from_exception
from PySide6.QtCore import QCoreApplication
from .popups import ErrorPopup
from sentry_sdk import Hub

import traceback
import pathlib
import inspect
import logging
import sys

def send_error_report(exc_info, flush=True):
    hub = Hub.current
    if hub.client is not None:
        hub.capture_event(*event_from_exception(exc_info))
        if flush:
            hub.flush()

def handle_exception(exc_type, exc_value, trace):
    try:
        exc_tuple = (exc_type, exc_value, trace)
        error_message = ''.join(traceback.format_exception(*exc_tuple))

        popup = ErrorPopup(error_message)
        popup.exec()

        if popup.sending:
            send_error_report(exc_tuple)

        stacks = inspect.stack()
        if len(stacks) >= 2:
            stack = stacks[1]
            module = inspect.getmodule(stack.frame)
            if module:
                module_name = module.__name__
            else:
                path = pathlib.Path(stack.filename)
                module_name = f"{path.parent.name}.{path.stem}"
        else:
            for filename in map(
                lambda frame: frame.filename,
                reversed(traceback.extract_tb(exc_tuple[-1]))
            ):
                path = pathlib.Path(filename)
                if path.parent.name == 'beskar' and not path.stem.startswith('__'):
                    module_name = f"beskar.{path.stem}"
                    break
            else:
                module_name = None

        if module_name in sys.modules:
            logger = logging.getLogger(module_name)
        else:
            logger = logging.getLogger('beskar.unknown')
            logger.warning(
                'Failed to determine which module caused '
                'the error in the upcoming logging message.'
            )

        logger.critical('The following error occured:', exc_info=exc_tuple)
    except Exception as second_error:
        second_error.__context__ = exc_value
        if popup.sending:
            send_error_report(second_error)
        logger = logging.getLogger('beskar.unknown')
        logger.error(
            'Two exceptions occured in handle_exception:',
            exc_info=second_error
        )
    finally:
        try:
            # NOTE: Trying to close the application even
            # if there is an error in the try block above
            # however, despite this we MUST exit the app
            # no matter what. In an abudance of caution
            # wrap this in a try finally block.
            QCoreApplication.quit()
        finally:
            sys.exit(1)
