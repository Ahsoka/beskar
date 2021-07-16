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
    # NOTE: This URL is the testing URL, don't forget to change to production URL
    'https://2645d9e6da7f4ae684bbfc162b78267f@o921203.ingest.sentry.io/5867522',
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
