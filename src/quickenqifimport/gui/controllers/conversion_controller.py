from PyQt6.QtWidgets import QMessageBox, QFileDialog
from PyQt6.QtCore import QObject, pyqtSlot
import csv
import os

from ..views.conversion_panel import ConversionPanel
from ...services.csv_to_qif_service import CSVToQIFService, CSVToQIFServiceError
from ...services.qif_to_csv_service import QIFToCSVService, QIFToCSVServiceError
from ...utils.template_utils import list_templates, load_template
from ...models.models import AccountType

class ConversionController(QObject):
    """Controller for the conversion panel."""
    
    def __init__(self, view: ConversionPanel, 
                csv_to_qif_service: CSVToQIFService,
                qif_to_csv_service: QIFToCSVService):
        """Initialize the conversion controller.
        
        Args:
            view: Conversion panel view
            csv_to_qif_service: Service for CSV to QIF conversion
            qif_to_csv_service: Service for QIF to CSV conversion
        """
        super().__init__()
        
        self.view = view
        self.csv_to_qif_service = csv_to_qif_service
        self.qif_to_csv_service = qif_to_csv_service
        
        self.current_template = None
        self.source_content = None
        self.target_content = None
        
        self._connect_signals()
        
        self._load_templates()
    
    def _connect_signals(self):
        """Connect signals to slots."""
        self.view.file_loaded.connect(self._on_file_loaded)
        self.view.template_selected.connect(self._on_template_selected)
        self.view.conversion_started.connect(self._on_conversion_started)
        self.view.conversion_completed.connect(self._on_conversion_completed)
    
    def _load_templates(self):
        """Load available templates."""
        try:
            template_names = list_templates()
            
            self.view.set_templates(template_names)
            
            if template_names:
                self._load_template(template_names[0])
        except Exception as e:
            self._show_error("Failed to load templates", str(e))
    
    def _load_template(self, template_name: str):
        """Load a template by name.
        
        Args:
            template_name: Name of the template to load
        """
        try:
            self.current_template = load_template(template_name)
            
            account_type_index = self._get_account_type_index(self.current_template.account_type)
            if account_type_index >= 0:
                self.view.account_type_combo.setCurrentIndex(account_type_index)
        except Exception as e:
            self._show_error("Failed to load template", str(e))
    
    def _get_account_type_index(self, account_type: AccountType) -> int:
        """Get the index of an account type in the account type combo box.
        
        Args:
            account_type: Account type to find
            
        Returns:
            int: Index of the account type, or -1 if not found
        """
        account_type_map = {
            AccountType.BANK: 0,
            AccountType.CASH: 1,
            AccountType.CREDIT_CARD: 2,
            AccountType.INVESTMENT: 3,
            AccountType.ASSET: 4,
            AccountType.LIABILITY: 5,
        }
        
        return account_type_map.get(account_type, -1)
    
    def _get_account_type_from_index(self, index: int) -> AccountType:
        """Get the account type from an index in the account type combo box.
        
        Args:
            index: Index in the combo box
            
        Returns:
            AccountType: Corresponding account type
        """
        account_type_map = {
            0: AccountType.BANK,
            1: AccountType.CASH,
            2: AccountType.CREDIT_CARD,
            3: AccountType.INVESTMENT,
            4: AccountType.ASSET,
            5: AccountType.LIABILITY,
        }
        
        return account_type_map.get(index, AccountType.BANK)
    
    @pyqtSlot(str, str)
    def _on_file_loaded(self, file_path: str, file_type: str):
        """Handle file loaded signal.
        
        Args:
            file_path: Path to the loaded file
            file_type: Type of the loaded file ('csv', 'qif', or 'unknown')
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.source_content = file.read()
            
            if file_type == 'csv':
                self._preview_csv(self.source_content)
            elif file_type == 'qif':
                self._preview_qif(self.source_content)
            else:
                self._show_error("Unknown file type", f"The file type '{file_type}' is not supported.")
        except Exception as e:
            self._show_error("Failed to load file", str(e))
    
    def _preview_csv(self, csv_content: str):
        """Preview CSV content in the source table.
        
        Args:
            csv_content: CSV content to preview
        """
        try:
            reader = csv.reader(csv_content.splitlines())
            rows = list(reader)
            
            if not rows:
                self._show_error("Empty CSV file", "The CSV file is empty.")
                return
            
            headers = rows[0]
            data = rows[1:]
            
            self.view.set_source_data(headers, data)
        except Exception as e:
            self._show_error("Failed to preview CSV", str(e))
    
    def _preview_qif(self, qif_content: str):
        """Preview QIF content in the source table.
        
        Args:
            qif_content: QIF content to preview
        """
        try:
            lines = qif_content.splitlines()
            headers = ["QIF Content"]
            data = [[line] for line in lines[:100]]  # Limit to 100 lines
            
            self.view.set_source_data(headers, data)
        except Exception as e:
            self._show_error("Failed to preview QIF", str(e))
    
    @pyqtSlot(str)
    def _on_template_selected(self, template_name: str):
        """Handle template selected signal.
        
        Args:
            template_name: Name of the selected template
        """
        self._load_template(template_name)
    
    @pyqtSlot()
    def _on_conversion_started(self):
        """Handle conversion started signal."""
        try:
            source_format = self.view.get_source_format()
            target_format = self.view.get_target_format()
            
            source_file_path = self.view.source_file_path
            target_file_path = self.view.target_file_path
            
            if not source_file_path:
                self._show_error("No source file", "Please select a source file.")
                return
            
            if not target_file_path:
                self._show_error("No target file", "Please select a target file.")
                return
            
            if not self.current_template:
                self._show_error("No template", "Please select a template.")
                return
            
            self.view.set_progress(10)
            
            if source_format == 'csv' and target_format == 'qif':
                self._convert_csv_to_qif(source_file_path, target_file_path)
            elif source_format == 'qif' and target_format == 'csv':
                self._convert_qif_to_csv(source_file_path, target_file_path)
            else:
                self._show_error("Invalid conversion", f"Conversion from {source_format} to {target_format} is not supported.")
                return
            
            self.view.set_progress(100)
            
            self._show_info("Conversion complete", f"The file has been converted and saved to {target_file_path}.")
        except Exception as e:
            self._show_error("Conversion failed", str(e))
            self.view.set_progress(0)
    
    def _convert_csv_to_qif(self, source_file_path: str, target_file_path: str):
        """Convert CSV to QIF.
        
        Args:
            source_file_path: Path to the source CSV file
            target_file_path: Path to the target QIF file
        """
        try:
            self.view.set_progress(30)
            
            self.csv_to_qif_service.convert_csv_file_to_qif_file(
                source_file_path, self.current_template, target_file_path
            )
            
            self.view.set_progress(90)
        except CSVToQIFServiceError as e:
            raise Exception(f"CSV to QIF conversion failed: {str(e)}")
    
    def _convert_qif_to_csv(self, source_file_path: str, target_file_path: str):
        """Convert QIF to CSV.
        
        Args:
            source_file_path: Path to the source QIF file
            target_file_path: Path to the target CSV file
        """
        try:
            self.view.set_progress(30)
            
            self.qif_to_csv_service.convert_qif_file_to_csv_file(
                source_file_path, self.current_template, target_file_path
            )
            
            self.view.set_progress(90)
        except QIFToCSVServiceError as e:
            raise Exception(f"QIF to CSV conversion failed: {str(e)}")
    
    @pyqtSlot()
    def _on_conversion_completed(self):
        """Handle conversion completed signal."""
        pass
    
    def open_file(self, file_path: str, file_type: str):
        """Open a file.
        
        Args:
            file_path: Path to the file to open
            file_type: Type of the file ('csv', 'qif', or 'unknown')
        """
        self.view.source_file_edit.setText(file_path)
        self.view.source_file_path = file_path
        self.view.source_file_type = file_type
        
        base_path, _ = os.path.splitext(file_path)
        if file_type == 'csv':
            target_file_path = f"{base_path}.qif"
            self.view.csv_to_qif_radio.setChecked(True)
        elif file_type == 'qif':
            target_file_path = f"{base_path}.csv"
            self.view.qif_to_csv_radio.setChecked(True)
        else:
            target_file_path = f"{base_path}.out"
        
        self.view.target_file_edit.setText(target_file_path)
        self.view.target_file_path = target_file_path
        
        self.view.preview_button.setEnabled(True)
        
        self._on_file_loaded(file_path, file_type)
    
    def convert(self, source_format: str, target_format: str):
        """Perform conversion.
        
        Args:
            source_format: Source format ('csv' or 'qif')
            target_format: Target format ('csv' or 'qif')
        """
        self.view.conversion_started.emit()
    
    def _show_error(self, title: str, message: str):
        """Show error message.
        
        Args:
            title: Error title
            message: Error message
        """
        QMessageBox.critical(self.view, title, message)
    
    def _show_info(self, title: str, message: str):
        """Show information message.
        
        Args:
            title: Information title
            message: Information message
        """
        QMessageBox.information(self.view, title, message)
    
    def _show_warning(self, title: str, message: str):
        """Show warning message.
        
        Args:
            title: Warning title
            message: Warning message
        """
        QMessageBox.warning(self.view, title, message)
