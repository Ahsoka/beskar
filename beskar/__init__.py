from sentry_sdk.integrations.logging import LoggingIntegration
from PyQt6.QtWidgets import QApplication
from .constants import __version__

import sys
import logging
import platform
import darkdetect
import sentry_sdk

sys_info = {
    'name': platform.system(),
    'version': platform.version(),
    'theme': darkdetect.theme()
}

sentry_sdk.set_context('os', sys_info)

def before_breadcrumbs(crumb, hint):
    if crumb['message'] == 'The following error occured:':
        return None
    return crumb

sentry_sdk.init(
    'https://f6c12472ccb949aaa9cc7c752f8aeb9a@o921203.ingest.sentry.io/5867524',
    environment='production' if getattr(sys, 'frozen', False) else 'development',
    integrations=(LoggingIntegration(logging.DEBUG, None),),
    before_breadcrumb=before_breadcrumbs,
    default_integrations=False,
    traces_sample_rate=1.0,
    release=__version__
)

from .gui import BeskarWindow

app = QApplication(sys.argv)
window = BeskarWindow()
