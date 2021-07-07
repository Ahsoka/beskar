pyinstaller --name "Beskar" ^
    --clean ^
    --noconfirm ^
    --icon "beskar\images\beskar-icon.ico" ^
    --paths "C:\ProgramData\Anaconda3\Lib\site-packages\PyQt6\Qt6\bin" ^
    --paths "C:\ProgramData\Anaconda3\Lib\site-packages\PyQt6\Qt6\plugins\platforms" ^
    --hidden-import "PyQt6.sip" --hidden-import "PyQt6.QtPrintSupport" ^
    --add-data "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\beskar\images;images" ^
    --add-data "C:\ProgramData\Anaconda3\Lib\site-packages\PyQt6\Qt6\plugins\platforms;platforms" ^
    --add-data "C:\ProgramData\Anaconda3\Lib\site-packages\PyQt6\Qt6\plugins\styles;styles" run.py

REM Reference: https://stackoverflow.com/questions/66286229/create-pyqt6-python-project-executable
