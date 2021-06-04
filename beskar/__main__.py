from PyQt6.QtWidgets import QApplication
from .gui import BeskarWindow

def main():
    import sys

    app = QApplication(sys.argv)
    window = BeskarWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
