import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings

from .views.main_window import MainWindow
from .controllers.main_controller import MainController
from ..utils.template_utils import create_default_templates

def main():
    """Main entry point for the QIF Converter application."""
    app = QApplication(sys.argv)
    app.setApplicationName("QIF Converter")
    app.setOrganizationName("QuickenQIFImport")
    app.setOrganizationDomain("github.com/mmarcus006/QuickenQIFImport")
    
    create_default_templates()
    
    main_window = MainWindow()
    main_controller = MainController(main_window)
    
    main_window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
