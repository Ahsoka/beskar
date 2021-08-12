from sentry_sdk.integrations.logging import LoggingIntegration
from PyQt6.QtWidgets import QApplication
from .constants import __version__
from .settings import Settings
from .utils import get_file

import sys
import logging
import platform
import darkdetect
import sentry_sdk

if getattr(sys, 'frozen', False):
    from .source import FrozenImporter, get_source_internet

    logger = logging.getLogger('beskar.source')

    for importer in sys.meta_path:
        if isinstance(importer, FrozenImporter):
            logger.info(
                "Detected PyInstaller's FrozenImporter class."
            )
            break
    else:
        logger.warning(
            "Failed to detect PyInstaller's FrozenImporter class."
        )
        importer = None

    if importer is not None:
        FrozenImporter.get_source = get_source_internet
        logger.info('Overrided FrozenImporter get_source function')

sys_info = {
    'name': platform.system(),
    'version': platform.version(),
    'theme': darkdetect.theme()
}
sentry_sdk.set_context('os', sys_info)

sentry_sdk.set_context('app', {'app_version': __version__})

def before_breadcrumbs(crumb, hint):
    if crumb['message'] == 'The following error occured:':
        return None
    return crumb

sentry_sdk.init(
    # Testing URL:
    # 'https://2645d9e6da7f4ae684bbfc162b78267f@o921203.ingest.sentry.io/5867522',

    # Production URL:
    'https://f6c12472ccb949aaa9cc7c752f8aeb9a@o921203.ingest.sentry.io/5867524',
    environment='production' if getattr(sys, 'frozen', False) else 'development',
    integrations=(LoggingIntegration(logging.DEBUG, None),),
    before_breadcrumb=before_breadcrumbs,
    default_integrations=False,
    traces_sample_rate=1.0,
    release=__version__
)

settings = Settings()

from .popups import StartUpPopup

app = QApplication(sys.argv)
app.setStyleSheet(get_file('main.css', 'qss', path=True).read_text())

startup = StartUpPopup()

update_thread = None
if sys.platform == 'win32':
    from .update import UpdateChecker, close_toasters
    from .handle_errors import handle_exception

    update_thread = UpdateChecker()
    update_thread.raise_exception.connect(lambda tup: handle_exception(*tup))
    update_thread.close_all_windows.connect(QApplication.closeAllWindows)
    app.aboutToQuit.connect(close_toasters)
    startup.rejected.connect(close_toasters)
