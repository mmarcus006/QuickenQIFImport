from PyQt6.QtWidgets import QMessageBox, QFileDialog
from PyQt6.QtCore import QObject, pyqtSlot

from ..views.main_window import MainWindow
from .conversion_controller import ConversionController
from .template_controller import TemplateController
from ...services.csv_to_qif_service import CSVToQIFService
from ...services.qif_to_csv_service import QIFToCSVService

class MainController(QObject):
    """Main application controller."""
    
    def __init__(self, main_window: MainWindow):
        """Initialize the main controller.
        
        Args:
            main_window: Main application window
        """
        super().__init__()
        
        self.main_window = main_window
        
        self.csv_to_qif_service = CSVToQIFService()
        self.qif_to_csv_service = QIFToCSVService()
        
        self.conversion_controller = ConversionController(
            self.main_window.conversion_panel,
            self.csv_to_qif_service,
            self.qif_to_csv_service
        )
        
        self.template_controller = TemplateController(
            self.main_window.template_manager
        )
        
        self._connect_signals()
    
    def _connect_signals(self):
        """Connect signals to slots."""
        self.main_window.file_opened.connect(self._on_file_opened)
        self.main_window.conversion_requested.connect(self._on_conversion_requested)
    
    @pyqtSlot(str, str)
    def _on_file_opened(self, file_path: str, file_type: str):
        """Handle file opened signal.
        
        Args:
            file_path: Path to the opened file
            file_type: Type of the opened file ('csv', 'qif', or 'unknown')
        """
        current_tab = self.main_window.tab_widget.currentWidget()
        
        if current_tab == self.main_window.conversion_panel:
            self.conversion_controller.open_file(file_path, file_type)
        elif current_tab == self.main_window.template_manager:
            self.template_controller.open_file(file_path)
    
    @pyqtSlot(str, str)
    def _on_conversion_requested(self, source_format: str, target_format: str):
        """Handle conversion requested signal.
        
        Args:
            source_format: Source format ('csv' or 'qif')
            target_format: Target format ('csv' or 'qif')
        """
        self.conversion_controller.convert(source_format, target_format)
    
    def show_error(self, title: str, message: str):
        """Show error message.
        
        Args:
            title: Error title
            message: Error message
        """
        QMessageBox.critical(self.main_window, title, message)
    
    def show_info(self, title: str, message: str):
        """Show information message.
        
        Args:
            title: Information title
            message: Information message
        """
        QMessageBox.information(self.main_window, title, message)
    
    def show_warning(self, title: str, message: str):
        """Show warning message.
        
        Args:
            title: Warning title
            message: Warning message
        """
        QMessageBox.warning(self.main_window, title, message)
