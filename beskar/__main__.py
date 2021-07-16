from sentry_sdk.utils import event_from_exception
from .popups import ErrorPopup
from sentry_sdk import Hub
from . import app, window

import sys
import traceback

def handle_exception(exc_type, exc_value, trace):
    error_message = ''.join(traceback.format_exception(exc_type, exc_value, trace))

    popup = ErrorPopup(window, error_message)
    popup.exec()

    if popup.sending:
        hub = Hub.current
        if hub.client is not None:
            hub.capture_event(*event_from_exception((exc_type, exc_value, trace)))
            hub.flush()

    sys.exit(error_message)

def main():
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    sys.excepthook = handle_exception
    main()
