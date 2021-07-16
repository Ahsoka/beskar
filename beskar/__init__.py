from PyQt6.QtWidgets import QApplication
from .constants import __version__

import sys
import platform
import darkdetect
import sentry_sdk

sys_info = {
    'name': platform.system(),
    'version': platform.version(),
    'theme': darkdetect.theme()
}

sentry_sdk.set_context('os', sys_info)

sentry_sdk.init(
    # NOTE: This URL is the testing URL, don't forget to change to production URL
    'https://2645d9e6da7f4ae684bbfc162b78267f@o921203.ingest.sentry.io/5867522',
    traces_sample_rate=1.0,
    environment='production' if getattr(sys, 'frozen', False) else 'development',
    release=__version__,
    default_integrations=False
)

from .gui import BeskarWindow

app = QApplication(sys.argv)
window = BeskarWindow()
