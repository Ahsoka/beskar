from PyQt6.QtWidgets import QApplication
from .gui import BeskarWindow
# from .side_bar import Window

def main():
    import sys

    app = QApplication(sys.argv)
    # window = Window()
    window = BeskarWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
