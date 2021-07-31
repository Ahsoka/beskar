from .utils import get_file, error_to_exc_tuple
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication
from urllib3.exceptions import HTTPError
from .constants import __version__
from typing import Callable, Union
from . import settings

import re
import zroya
import urllib3
import logging
import warnings
import functools
import darkdetect
import subprocess
import webbrowser

logger = logging.getLogger(__name__)

pool = urllib3.PoolManager(num_pools=2)

setup_exe_dir = settings.settings_path.parent / 'setup-exes'

latest_url = 'https://github.com/Ahsoka/beskar/releases/latest'

@functools.lru_cache
def zroya_init(
    app_name='Beskar',
    company_name='Ahsoka',
    product_name='Beskar',
    sub_product='main',
    version=__version__
) -> bool:
    init = zroya.init(
        app_name=app_name,
        company_name=company_name,
        product_name=product_name,
        sub_product=sub_product,
        version=version
    )
    if init:
        logger.info('Succesfully initialized zroya.')
    else:
        logger.warning('Initializing zroya for toaster notifications failed.')
    return init

def download(version):
    filename = f'beskar-install-{version}-64bit.exe'

    download = pool.request(
        'GET',
        'https://github.com/Ahsoka/beskar/releases/download/'
        f'{version}/{filename}',
        preload_content=False
    )

    if not setup_exe_dir.exists():
        setup_exe_dir.mkdir()

    with (setup_exe_dir / filename).open(mode='wb') as exe:
        for chunk in download.stream(4096):
            exe.write(chunk)
        download.release_conn()

    return filename

def on_toaster_interaction(notification_id, action_id, setup_exe, update_checker: 'UpdateChecker'):
    try:
        if action_id == 0:
            QApplication.setQuitOnLastWindowClosed(False)

            update_checker.close_all_windows.emit()

            warnings.filterwarnings(
                'ignore',
                r'subprocess \d+ is still running',
                category=ResourceWarning
            )
            subprocess.Popen(f'{(setup_exe_dir / setup_exe).absolute()}')
            QApplication.quit()
        elif action_id == 1:
            webbrowser.open(latest_url)
            toaster = create_toaster(
                second_line='Thanks for checking out the update notes!',
                third_line="This will be here for when you are ready to update!",
                toaster_type=zroya.TemplateType.Text4,
                whats_new=False
            )
            show(toaster, update_checker, setup_exe)
    except Exception as error:
        update_checker.raise_exception.emit(error_to_exc_tuple(error))

def create_toaster(
    first_line: str = 'Beskar',
    second_line: str = 'An update for Beskar is available.',
    new_version: str = None,
    third_line: str = None,
    update_action: bool = True,
    whats_new: bool = True,
    toaster_type=zroya.TemplateType.ImageAndText4
):
    if zroya_init():
        toaster = zroya.Template(toaster_type)
        toaster.setFirstLine(first_line)
        toaster.setSecondLine(second_line)
        if third_line:
            toaster.setThirdLine(third_line)
        else:
            if new_version is None:
                raise TypeError('new_version and third_line cannot both be None.')
            else:
                toaster.setThirdLine(f'{__version__} ➡ {new_version}')

        if darkdetect.isDark():
            icon_loc = get_file('beskar-icon-white.png')
        else:
            icon_loc = get_file('beskar-icon.png')
        toaster.setImage(icon_loc)

        if update_action:
            toaster.addAction('Update')
        if whats_new:
            toaster.addAction("What's New?")

        return toaster

def show(
    toaster,
    update_checker: 'UpdateChecker',
    setup_exe_filename: str,
    on_action: Callable = on_toaster_interaction,
    on_dismiss: Callable = None,
    on_fail: Callable = None
) -> Union[bool, int]:
    on_action_partial = functools.partial(on_action, setup_exe=setup_exe_filename, update_checker=update_checker)

    kwargs = {
        'on_action': on_action_partial,
        'on_click': functools.partial(on_action_partial, action_id=0)
    }
    if on_dismiss:
        kwargs['on_dismiss'] = on_dismiss
    if on_fail:
        kwargs['on_fail'] = on_fail

    return zroya.show(toaster, **kwargs)


class UpdateChecker(QThread):
    raise_exception = pyqtSignal(tuple)

    close_all_windows = pyqtSignal()

    def run(self):
        self.check_for_update()

    def check_for_update(self):
        try:
            downloading = False
            request = pool.request('GET', latest_url)
            match = re.search(r'v\d+.\d+.\d+', request.geturl())
            if match and match[0] > __version__:
                new_version = match[0]
                logger.info(f'New version {new_version} of Beskar was detected.')
                downloading = True
                setup_exe_filename = download(new_version)
                logger.info(f'Succesfully installed the setup exe for {new_version}.')
                toaster = create_toaster(new_version=new_version)
                if show(toaster, self, setup_exe_filename):
                    logger.info('Toaster notification for the available update was succesfully shown.')
                else:
                    logger.warning('Failed to show toaster notification for the avaliable update.')
        except HTTPError as error:
            if downloading:
                msg = f'Error occured while downloading the setup-exe.'
                for exe in setup_exe_dir.iterdir():
                    if exe.is_file():
                        exe.unlink()
            else:
                msg = f'Failed to connect to the internet and check for any updates.',
            logger.warning(msg, exc_info=error)
        except IndexError as error:
            logger.error(
                'Ignoring IndexError with re.Match object, this should not have happened.',
                exc_info=error
            )
        except Exception as error:
            self.raise_exception.emit(error_to_exc_tuple(error))