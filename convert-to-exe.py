from PyInstaller.__main__ import run

import PyQt6
import pathlib

pyqt6_dir = pathlib.Path(PyQt6.__file__).parent

if __name__ == '__main__':
    run([
        'run.py',
        '--name', 'Beskar',
        '--clean',
        '--noconfirm',
        '--icon', r'beskar\images\beskar-icon.ico',
        '--paths', f'{pyqt6_dir / "Qt6" / "bin"}',
        '--paths', f'{pyqt6_dir / "Qt6" / "plugins" / "platforms"}',
        '--hidden-import', 'PyQt6.sip',
        '--hidden-import', 'PyQt6.QtPrintSupport',
        '--add-data', r'beskar\images;images',
        '--add-data', f'{pyqt6_dir / "Qt6" / "plugins" / "platforms"};platforms',
        '--add-data', f'{pyqt6_dir / "Qt6" / "plugins" / "styles"};styles'
    ])
