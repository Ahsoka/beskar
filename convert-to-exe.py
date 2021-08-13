from PyInstaller.__main__ import run

import PyQt6
import certifi
import pathlib

pyqt6_dir = pathlib.Path(PyQt6.__file__).parent
certifi_dir = pathlib.Path(certifi.__file__).parent

if __name__ == '__main__':
    run([
        'run.py',
        '--name', 'Beskar',
        '--clean',
        '--noconfirm',
        '--noconsole',
        '--icon', r'beskar\images\beskar-icon.ico',
        '--paths', f'{pyqt6_dir / "Qt6" / "bin"}',
        '--paths', f'{pyqt6_dir / "Qt6" / "plugins" / "platforms"}',
        '--hidden-import', 'PyQt6.sip',
        '--hidden-import', 'PyQt6.QtPrintSupport',
        '--add-data', r'beskar\images;images',
        '--add-data', r'beskar\qss;qss',
        '--add-data', r'beskar\fonts;fonts',
        '--add-data', f'{pyqt6_dir / "Qt6" / "plugins" / "platforms"};platforms',
        '--add-data', f'{pyqt6_dir / "Qt6" / "plugins" / "styles"};styles',
        '--add-data', r'beskar\desc;desc',
        '--add-data', f'{certifi_dir / "cacert.pem"};certifi'
    ])
