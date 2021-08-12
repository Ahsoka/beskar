from .utils import get_file, error_to_exc_tuple
from PyQt6.QtCore import QThread, pyqtSignal
from urllib3.exceptions import HTTPError
from typing import Callable, Union, List
from .constants import __version__
from . import settings

import re
import zroya
import hashlib
import urllib3
import logging
import warnings
import functools
import darkdetect
import subprocess
import webbrowser

# NOTE: Recently discovered the winrt package
# which allows access to Windows UWP Namespaces
# directly in Python. This would enable even more
# control over toasters than with zroya/WinToaster
# If you are up for it, see here: https://pypi.org/project/winrt
# and here: https://github.com/Microsoft/xlang/tree/master/src/package/pywinrt/projection

logger = logging.getLogger(__name__)

pool = urllib3.PoolManager(num_pools=2)

setup_exe_dir = settings.settings_path.parent / 'setup-exes'

latest_url = 'https://github.com/Ahsoka/beskar/releases/latest'

toasters: List[int] = []

def get_exe_file_name(version: str):
    return f'beskar-install-{version}-64bit.exe'

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
    filename = get_exe_file_name(version)

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

def on_toaster_interaction(notification_id, action_id, setup_exe, update_checker: 'UpdateChecker'):
    try:
        if action_id == 0:
            update_checker.close_all_windows.emit()

            warnings.filterwarnings(
                'ignore',
                r'subprocess \d+ is still running',
                category=ResourceWarning
            )
            subprocess.Popen(f'{(setup_exe_dir / setup_exe).absolute()}')
            pool.clear()
            update_checker.quit()
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

    toaster_id = zroya.show(toaster, **kwargs)
    if isinstance(toaster_id, int):
        toasters.append(toaster_id)
    return toaster_id

def close_toasters():
    pool.clear()
    for toaster_id in toasters:
        # NOTE: The version of zroya on PyPi currently has a bug
        # in it that prevents the `hide` function from working correctly.
        # I was able to rebuild a new version of zroya with a working
        # hide function thanks to this issue: https://github.com/malja/zroya/issues/14
        if zroya.hide(nid=toaster_id):
            logger.info(f'Successfully closed toaster {toaster_id}.')
        else:
            logger.warning(f'Failed to close toaster {toaster_id}.')


class UpdateChecker(QThread):
    raise_exception = pyqtSignal(tuple)

    close_all_windows = pyqtSignal()

    def run(self):
        self.check_for_update()

    def check_for_update(self):
        try:
            downloading = False
            need_to_install = True
            check_hash = False

            request = pool.request('GET', latest_url)
            match = re.search(r'v\d+.\d+.\d+', request.geturl())
            if match and match[0] > __version__:
                new_version = match[0]
                logger.info(f'New version {new_version} of Beskar was detected.')
                setup_exe_filename = get_exe_file_name(new_version)
                setup_exe = setup_exe_dir / setup_exe_filename
                if setup_exe.exists():
                    # SHA256 code from:
                    # https://www.quickprogrammingtips.com/python/how-to-calculate-sha256-hash-of-a-file-in-python.html
                    sha256_hash = hashlib.sha256()
                    with setup_exe.open(mode='rb') as file:
                        for chunk in iter(lambda: file.read(4096), b''):
                            sha256_hash.update(chunk)
                    try:
                        check_hash = True
                        if pool.request(
                            'GET',
                            f'https://raw.githubusercontent.com/Ahsoka/beskar/main/sha256-hashes/{new_version}.txt'
                        ).data.decode('UTF-8')[:-1] == sha256_hash.hexdigest():
                            need_to_install = False
                            logger.info(f'Detected the setup exe for version {new_version} is already installed.')
                    except UnicodeDecodeError as error:
                        logger.warning(
                            f'Error occured while trying to decode the SHA256 hash for {new_version}.',
                            exc_info=error
                        )

                if need_to_install:
                    downloading = True
                    download(new_version)
                    logger.info(f'Succesfully installed the setup exe for {new_version}.')

                toaster = create_toaster(new_version=new_version)
                if show(toaster, self, setup_exe_filename):
                    logger.info('Toaster notification for the available update was succesfully shown.')
                else:
                    logger.warning('Failed to show toaster notification for the avaliable update.')
        except HTTPError as error:
            if downloading:
                msg = 'Error occured while downloading the setup-exe.'
                for exe in setup_exe_dir.iterdir():
                    if exe.is_file():
                        exe.unlink()
            elif check_hash:
                msg = 'Error occured while trying to retreive SHA256 hash.'
            else:
                msg = 'Failed to connect to the internet and check for any updates.'
            logger.warning(msg, exc_info=error)
        except IndexError as error:
            logger.error(
                'Ignoring IndexError with re.Match object, this should not have happened.',
                exc_info=error
            )
        except Exception as error:
            self.raise_exception.emit(error_to_exc_tuple(error))
