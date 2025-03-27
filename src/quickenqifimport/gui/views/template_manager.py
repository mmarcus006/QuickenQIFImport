from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QComboBox, QLineEdit, QTableView, QFileDialog,
    QGroupBox, QRadioButton, QSplitter, QTabWidget, QProgressBar,
    QCheckBox, QSpinBox, QMessageBox, QDialog, QFormLayout,
    QListWidget, QListWidgetItem, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QStandardItemModel, QStandardItem

from ...models.models import CSVTemplate, AccountType

class TemplateManager(QWidget):
    """Widget for managing CSV templates."""
    
    template_selected = pyqtSignal(str)  # template_name
    template_created = pyqtSignal(CSVTemplate)
    template_updated = pyqtSignal(CSVTemplate)
    template_deleted = pyqtSignal(str)  # template_name
    
    def __init__(self):
        """Initialize the template manager."""
        super().__init__()
        
        self.templates = {}
        self.current_template = None
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the UI components."""
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        
        self._create_template_list_section(main_layout)
        
        self._create_template_details_section(main_layout)
    
    def _create_template_list_section(self, parent_layout):
        """Create the template list section.
        
        Args:
            parent_layout: Parent layout to add the section to
        """
        list_widget = QWidget()
        list_layout = QVBoxLayout()
        list_widget.setLayout(list_layout)
        
        list_label = QLabel("Templates:")
        self.template_list = QListWidget()
        self.template_list.setMinimumWidth(200)
        
        button_layout = QHBoxLayout()
        self.new_button = QPushButton("New")
        self.delete_button = QPushButton("Delete")
        self.import_button = QPushButton("Import")
        self.export_button = QPushButton("Export")
        
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.export_button)
        
        list_layout.addWidget(list_label)
        list_layout.addWidget(self.template_list)
        list_layout.addLayout(button_layout)
        
        parent_layout.addWidget(list_widget, 1)
        
        self.template_list.currentItemChanged.connect(self._on_template_selected)
        self.new_button.clicked.connect(self._on_new_template)
        self.delete_button.clicked.connect(self._on_delete_template)
        self.import_button.clicked.connect(self._on_import_template)
        self.export_button.clicked.connect(self._on_export_template)
    
    def _create_template_details_section(self, parent_layout):
        """Create the template details section.
        
        Args:
            parent_layout: Parent layout to add the section to
        """
        details_widget = QWidget()
        details_layout = QVBoxLayout()
        details_widget.setLayout(details_layout)
        
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.description_edit = QLineEdit()
        self.account_type_combo = QComboBox()
        self.account_type_combo.addItems(["Bank", "Cash", "Credit Card", "Investment", "Asset", "Liability"])
        self.delimiter_edit = QLineEdit()
        self.date_format_edit = QLineEdit()
        self.has_header_check = QCheckBox("Has Header")
        self.skip_rows_spin = QSpinBox()
        self.skip_rows_spin.setMinimum(0)
        self.skip_rows_spin.setMaximum(100)
        
        form_layout.addRow("Name:", self.name_edit)
        form_layout.addRow("Description:", self.description_edit)
        form_layout.addRow("Account Type:", self.account_type_combo)
        form_layout.addRow("Delimiter:", self.delimiter_edit)
        form_layout.addRow("Date Format:", self.date_format_edit)
        form_layout.addRow("", self.has_header_check)
        form_layout.addRow("Skip Rows:", self.skip_rows_spin)
        
        mapping_group = QGroupBox("Field Mapping")
        mapping_layout = QGridLayout()
        mapping_group.setLayout(mapping_layout)
        
        self.mapping_table = QTableView()
        self.mapping_model = QStandardItemModel()
        self.mapping_model.setHorizontalHeaderLabels(["Field", "CSV Column"])
        self.mapping_table.setModel(self.mapping_model)
        
        mapping_layout.addWidget(self.mapping_table, 0, 0, 1, 2)
        
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        details_layout.addLayout(form_layout)
        details_layout.addWidget(mapping_group)
        details_layout.addLayout(button_layout)
        
        parent_layout.addWidget(details_widget, 2)
        
        self.save_button.clicked.connect(self._on_save_template)
        self.cancel_button.clicked.connect(self._on_cancel)
    
    def _on_template_selected(self, current, previous):
        """Handle template selection changed event.
        
        Args:
            current: Current item
            previous: Previous item
        """
        if current:
            template_name = current.text()
            self.template_selected.emit(template_name)
    
    def _on_new_template(self):
        """Handle new template button click event."""
        self.name_edit.clear()
        self.description_edit.clear()
        self.account_type_combo.setCurrentIndex(0)
        self.delimiter_edit.setText(",")
        self.date_format_edit.setText("%Y-%m-%d")
        self.has_header_check.setChecked(True)
        self.skip_rows_spin.setValue(0)
        
        self.mapping_model.clear()
        self.mapping_model.setHorizontalHeaderLabels(["Field", "CSV Column"])
        
        self._add_default_fields(AccountType.BANK)
        
        self.current_template = None
    
    def _on_delete_template(self):
        """Handle delete template button click event."""
        current_item = self.template_list.currentItem()
        if current_item:
            template_name = current_item.text()
            
            reply = QMessageBox.question(
                self,
                "Confirm Deletion",
                f"Are you sure you want to delete the template '{template_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.template_deleted.emit(template_name)
    
    def _on_import_template(self):
        """Handle import template button click event."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("YAML Files (*.yaml);;All Files (*.*)")
        
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                file_path = file_paths[0]
                
                pass
    
    def _on_export_template(self):
        """Handle export template button click event."""
        current_item = self.template_list.currentItem()
        if current_item:
            template_name = current_item.text()
            
            file_dialog = QFileDialog(self)
            file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            file_dialog.setNameFilter("YAML Files (*.yaml);;All Files (*.*)")
            file_dialog.setDefaultSuffix("yaml")
            
            if file_dialog.exec():
                file_paths = file_dialog.selectedFiles()
                if file_paths:
                    file_path = file_paths[0]
                    
                    pass
    
    def _on_save_template(self):
        """Handle save template button click event."""
        name = self.name_edit.text()
        description = self.description_edit.text()
        account_type_index = self.account_type_combo.currentIndex()
        account_type = self._get_account_type_from_index(account_type_index)
        delimiter = self.delimiter_edit.text()
        date_format = self.date_format_edit.text()
        has_header = self.has_header_check.isChecked()
        skip_rows = self.skip_rows_spin.value()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Template name is required.")
            return
        
        if not delimiter:
            QMessageBox.warning(self, "Validation Error", "Delimiter is required.")
            return
        
        field_mapping = {}
        for row in range(self.mapping_model.rowCount()):
            field_item = self.mapping_model.item(row, 0)
            column_item = self.mapping_model.item(row, 1)
            
            if field_item and column_item:
                field = field_item.text()
                column = column_item.text()
                
                if field and column:
                    field_mapping[field] = column
        
        template = CSVTemplate(
            name=name,
            description=description,
            account_type=account_type,
            delimiter=delimiter,
            date_format=date_format,
            has_header=has_header,
            skip_rows=skip_rows,
            field_mapping=field_mapping,
            amount_columns=[],
            amount_multiplier={},
            category_format="Category:Subcategory",
            detect_transfers=True,
            transfer_pattern=r"\[(.*?)\]"
        )
        
        if self.current_template:
            self.template_updated.emit(template)
        else:
            self.template_created.emit(template)
    
    def _on_cancel(self):
        """Handle cancel button click event."""
        current_item = self.template_list.currentItem()
        if current_item:
            self._on_template_selected(current_item, None)
    
    def _add_default_fields(self, account_type: AccountType):
        """Add default fields to the mapping table based on account type.
        
        Args:
            account_type: Account type to add fields for
        """
        self.mapping_model.clear()
        self.mapping_model.setHorizontalHeaderLabels(["Field", "CSV Column"])
        
        if account_type == AccountType.BANK or account_type == AccountType.CASH or \
           account_type == AccountType.CREDIT_CARD or account_type == AccountType.ASSET or \
           account_type == AccountType.LIABILITY:
            fields = [
                ("date", "Date"),
                ("amount", "Amount"),
                ("payee", "Description"),
                ("number", "Reference"),
                ("memo", "Memo"),
                ("category", "Category"),
                ("account", "Account Name"),
                ("cleared_status", "Status")
            ]
        else:
            fields = [
                ("date", "Date"),
                ("action", "Action"),
                ("security", "Security"),
                ("quantity", "Quantity"),
                ("price", "Price"),
                ("amount", "Amount"),
                ("commission", "Commission"),
                ("payee", "Description"),
                ("category", "Category"),
                ("account", "Account"),
                ("memo", "Memo"),
                ("cleared_status", "Status")
            ]
        
        for field, column in fields:
            field_item = QStandardItem(field)
            column_item = QStandardItem(column)
            
            self.mapping_model.appendRow([field_item, column_item])
        
        self.mapping_table.resizeColumnsToContents()
    
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
    
    def set_templates(self, templates: dict):
        """Set the available templates.
        
        Args:
            templates: Dictionary of template names to CSVTemplate objects
        """
        self.templates = templates
        
        self.template_list.clear()
        
        for name in sorted(templates.keys()):
            self.template_list.addItem(name)
        
        if self.template_list.count() > 0:
            self.template_list.setCurrentRow(0)
    
    def set_template(self, template: CSVTemplate):
        """Set the current template.
        
        Args:
            template: Template to display
        """
        self.current_template = template
        
        self.name_edit.setText(template.name)
        self.description_edit.setText(template.description or "")
        
        account_type_index = self._get_account_type_index(template.account_type)
        if account_type_index >= 0:
            self.account_type_combo.setCurrentIndex(account_type_index)
        
        self.delimiter_edit.setText(template.delimiter)
        self.date_format_edit.setText(template.date_format or "")
        self.has_header_check.setChecked(template.has_header)
        self.skip_rows_spin.setValue(template.skip_rows)
        
        self.mapping_model.clear()
        self.mapping_model.setHorizontalHeaderLabels(["Field", "CSV Column"])
        
        for field, column in template.field_mapping.items():
            field_item = QStandardItem(field)
            column_item = QStandardItem(column)
            
            self.mapping_model.appendRow([field_item, column_item])
        
        self.mapping_table.resizeColumnsToContents()
