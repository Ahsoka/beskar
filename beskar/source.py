from urllib3.response import HTTPResponse
from urllib3.exceptions import HTTPError
from __main__ import pyimod03_importers
from .settings import logging_dir
from .logs import setUpLogger

import sys
import urllib3

logger = setUpLogger(__name__, logging_dir, file_name='source.log')

FrozenImporter = pyimod03_importers.FrozenImporter

og_get_source = FrozenImporter.get_source

pool = urllib3.PoolManager(num_pools=5)

github = {
    'darkdetect': ('albertosottile', 'darkdetect'),
    'nidaqmx': ('ni', 'nidaqmx-python', '0.5.7'),
    'numpy': ('numpy',) * 2
}

def get_source_internet(self, fullname: str):
    og_result = og_get_source(self, fullname)
    if og_result:
        return og_result
    logger.warning(
        'Failed to find source code using og_get_source function.'
    )
    package_name, *rest = fullname.split('.')
    module = sys.modules.get(package_name)


    if module and package_name in github:
        if hasattr(module, '__version__'):
            __version__: str = module.__version__
            if not __version__.startswith('v'):
                __version__ = 'v' + __version__
        else:
            __version__ = github[package_name][2]

        if len(rest) == 0:
            rest = ['__init__.py']
        elif rest[-1][-3:] != '.py':
            rest[-1] += '.py'
        try:
            url = (
                f'https://raw.githubusercontent.com/{github[package_name][0]}/'
                f'{github[package_name][1]}/{__version__}/{package_name}'
                f"/{'/'.join(rest)}"
            )
            request: HTTPResponse  = pool.request('GET', url)
            source = request.data.decode('UTF-8')
            if request.status >= 200 and request.status < 300:
                logger.info(f'Successfully retrieved source code for {fullname!r}.')
                return source
            else:
                logger.warning(
                    f'Failed to retrieve source code for {fullname!r}.',
                    extra={'url': url, 'status-code': request.status}
                )
        except (HTTPError, UnicodeError) as error:
            logger.warning(
                f'Failed to retrieve source code for {fullname!r}.',
                exc_info=error,
                extra={'url': url}
            )
    elif module is None:
        logger.warning(
        f'Failed to import module {package_name!r}.'
    )
    elif package_name not in github:
        logger.info(
            f'{package_name!r} is not a supported package for URL retrieval.'
        )
    else:
        logger.warning(
            f'Retrieving {fullname!r} failed for an unknown reason.'
        )
