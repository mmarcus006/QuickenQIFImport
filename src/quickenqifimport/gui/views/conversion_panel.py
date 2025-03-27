from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QComboBox, QLineEdit, QTableView, QFileDialog,
    QGroupBox, QRadioButton, QSplitter, QTabWidget, QProgressBar,
    QCheckBox, QSpinBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QStandardItemModel, QStandardItem

class ConversionPanel(QWidget):
    """Panel for CSV to QIF conversion."""
    
    file_loaded = pyqtSignal(str, str)  # file_path, file_type
    template_selected = pyqtSignal(str)  # template_name
    conversion_started = pyqtSignal()
    conversion_completed = pyqtSignal()
    
    def __init__(self):
        """Initialize the conversion panel."""
        super().__init__()
        
        self.source_file_path = None
        self.source_file_type = None
        self.target_file_path = None
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the UI components."""
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        self._create_conversion_type_section(main_layout)
        
        self._create_file_selection_section(main_layout)
        
        self._create_template_selection_section(main_layout)
        
        self._create_preview_section(main_layout)
        
        self._create_action_buttons(main_layout)
        
        self._create_progress_bar(main_layout)
    
    def _create_conversion_type_section(self, parent_layout):
        """Create the conversion type selection section.
        
        Args:
            parent_layout: Parent layout to add the section to
        """
        group_box = QGroupBox("Conversion Type")
        parent_layout.addWidget(group_box)
        
        layout = QHBoxLayout()
        group_box.setLayout(layout)
        
        self.csv_to_qif_radio = QRadioButton("CSV to QIF")
        self.qif_to_csv_radio = QRadioButton("QIF to CSV")
        
        self.csv_to_qif_radio.setChecked(True)
        
        layout.addWidget(self.csv_to_qif_radio)
        layout.addWidget(self.qif_to_csv_radio)
        
        self.csv_to_qif_radio.toggled.connect(self._on_conversion_type_changed)
        self.qif_to_csv_radio.toggled.connect(self._on_conversion_type_changed)
    
    def _create_file_selection_section(self, parent_layout):
        """Create the file selection section.
        
        Args:
            parent_layout: Parent layout to add the section to
        """
        group_box = QGroupBox("File Selection")
        parent_layout.addWidget(group_box)
        
        layout = QGridLayout()
        group_box.setLayout(layout)
        
        source_label = QLabel("Source File:")
        self.source_file_edit = QLineEdit()
        self.source_file_edit.setReadOnly(True)
        source_browse_button = QPushButton("Browse...")
        
        target_label = QLabel("Target File:")
        self.target_file_edit = QLineEdit()
        self.target_file_edit.setReadOnly(True)
        target_browse_button = QPushButton("Browse...")
        
        layout.addWidget(source_label, 0, 0)
        layout.addWidget(self.source_file_edit, 0, 1)
        layout.addWidget(source_browse_button, 0, 2)
        layout.addWidget(target_label, 1, 0)
        layout.addWidget(self.target_file_edit, 1, 1)
        layout.addWidget(target_browse_button, 1, 2)
        
        source_browse_button.clicked.connect(self._on_source_browse)
        target_browse_button.clicked.connect(self._on_target_browse)
    
    def _create_template_selection_section(self, parent_layout):
        """Create the template selection section.
        
        Args:
            parent_layout: Parent layout to add the section to
        """
        self.template_group_box = QGroupBox("Template Selection")
        parent_layout.addWidget(self.template_group_box)
        
        layout = QGridLayout()
        self.template_group_box.setLayout(layout)
        
        template_label = QLabel("Template:")
        self.template_combo = QComboBox()
        self.template_combo.setMinimumWidth(200)
        edit_template_button = QPushButton("Edit...")
        new_template_button = QPushButton("New...")
        
        account_type_label = QLabel("Account Type:")
        self.account_type_combo = QComboBox()
        self.account_type_combo.addItems(["Bank", "Cash", "Credit Card", "Investment", "Asset", "Liability"])
        
        layout.addWidget(template_label, 0, 0)
        layout.addWidget(self.template_combo, 0, 1)
        layout.addWidget(edit_template_button, 0, 2)
        layout.addWidget(new_template_button, 0, 3)
        layout.addWidget(account_type_label, 1, 0)
        layout.addWidget(self.account_type_combo, 1, 1)
        
        self.template_combo.currentIndexChanged.connect(self._on_template_selected)
        edit_template_button.clicked.connect(self._on_edit_template)
        new_template_button.clicked.connect(self._on_new_template)
        self.account_type_combo.currentIndexChanged.connect(self._on_account_type_changed)
    
    def _create_preview_section(self, parent_layout):
        """Create the preview section.
        
        Args:
            parent_layout: Parent layout to add the section to
        """
        group_box = QGroupBox("Preview")
        parent_layout.addWidget(group_box)
        
        layout = QVBoxLayout()
        group_box.setLayout(layout)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        source_widget = QWidget()
        source_layout = QVBoxLayout()
        source_widget.setLayout(source_layout)
        source_label = QLabel("Source Data:")
        self.source_table = QTableView()
        source_layout.addWidget(source_label)
        source_layout.addWidget(self.source_table)
        
        target_widget = QWidget()
        target_layout = QVBoxLayout()
        target_widget.setLayout(target_layout)
        target_label = QLabel("Target Data:")
        self.target_table = QTableView()
        target_layout.addWidget(target_label)
        target_layout.addWidget(self.target_table)
        
        splitter.addWidget(source_widget)
        splitter.addWidget(target_widget)
        
        splitter.setSizes([500, 500])
        
        self.source_model = QStandardItemModel()
        self.target_model = QStandardItemModel()
        
        self.source_table.setModel(self.source_model)
        self.target_table.setModel(self.target_model)
    
    def _create_action_buttons(self, parent_layout):
        """Create the action buttons.
        
        Args:
            parent_layout: Parent layout to add the buttons to
        """
        layout = QHBoxLayout()
        parent_layout.addLayout(layout)
        
        self.preview_button = QPushButton("Preview")
        self.convert_button = QPushButton("Convert")
        self.cancel_button = QPushButton("Cancel")
        
        layout.addStretch()
        layout.addWidget(self.preview_button)
        layout.addWidget(self.convert_button)
        layout.addWidget(self.cancel_button)
        
        self.preview_button.clicked.connect(self._on_preview)
        self.convert_button.clicked.connect(self._on_convert)
        self.cancel_button.clicked.connect(self._on_cancel)
        
        self.preview_button.setEnabled(False)
        self.convert_button.setEnabled(False)
    
    def _create_progress_bar(self, parent_layout):
        """Create the progress bar.
        
        Args:
            parent_layout: Parent layout to add the progress bar to
        """
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        parent_layout.addWidget(self.progress_bar)
    
    def _on_conversion_type_changed(self):
        """Handle conversion type changed event."""
        if self.csv_to_qif_radio.isChecked():
            self.source_file_edit.clear()
            self.target_file_edit.clear()
            self.source_file_path = None
            self.source_file_type = None
            self.target_file_path = None
            self.template_group_box.setEnabled(True)
        else:
            self.source_file_edit.clear()
            self.target_file_edit.clear()
            self.source_file_path = None
            self.source_file_type = None
            self.target_file_path = None
            self.template_group_box.setEnabled(True)
        
        self.source_model.clear()
        self.target_model.clear()
        
        self.preview_button.setEnabled(False)
        self.convert_button.setEnabled(False)
    
    def _on_source_browse(self):
        """Handle source browse button click event."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        
        if self.csv_to_qif_radio.isChecked():
            file_dialog.setNameFilter("CSV Files (*.csv);;All Files (*.*)")
        else:
            file_dialog.setNameFilter("QIF Files (*.qif);;All Files (*.*)")
        
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                file_path = file_paths[0]
                
                self.source_file_edit.setText(file_path)
                self.source_file_path = file_path
                
                if file_path.lower().endswith('.csv'):
                    self.source_file_type = 'csv'
                elif file_path.lower().endswith('.qif'):
                    self.source_file_type = 'qif'
                else:
                    self.source_file_type = 'unknown'
                
                base_path, _ = file_path.rsplit('.', 1)
                if self.csv_to_qif_radio.isChecked():
                    self.target_file_path = f"{base_path}.qif"
                else:
                    self.target_file_path = f"{base_path}.csv"
                self.target_file_edit.setText(self.target_file_path)
                
                self.preview_button.setEnabled(True)
                
                self.file_loaded.emit(file_path, self.source_file_type)
    
    def _on_target_browse(self):
        """Handle target browse button click event."""
        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        
        if self.csv_to_qif_radio.isChecked():
            file_dialog.setNameFilter("QIF Files (*.qif);;All Files (*.*)")
            file_dialog.setDefaultSuffix("qif")
        else:
            file_dialog.setNameFilter("CSV Files (*.csv);;All Files (*.*)")
            file_dialog.setDefaultSuffix("csv")
        
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                file_path = file_paths[0]
                
                self.target_file_edit.setText(file_path)
                self.target_file_path = file_path
    
    def _on_template_selected(self, index):
        """Handle template selection changed event.
        
        Args:
            index: Selected index
        """
        if index >= 0:
            template_name = self.template_combo.currentText()
            self.template_selected.emit(template_name)
    
    def _on_edit_template(self):
        """Handle edit template button click event."""
        template_name = self.template_combo.currentText()
        if template_name:
            pass
    
    def _on_new_template(self):
        """Handle new template button click event."""
        pass
    
    def _on_account_type_changed(self, index):
        """Handle account type selection changed event.
        
        Args:
            index: Selected index
        """
        pass
    
    def _on_preview(self):
        """Handle preview button click event."""
        pass
    
    def _on_convert(self):
        """Handle convert button click event."""
        self.conversion_started.emit()
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.preview_button.setEnabled(False)
        self.convert_button.setEnabled(False)
    
    def _on_cancel(self):
        """Handle cancel button click event."""
        self.progress_bar.setVisible(False)
        
        self.preview_button.setEnabled(True)
        self.convert_button.setEnabled(True)
    
    def set_templates(self, templates):
        """Set the available templates.
        
        Args:
            templates: List of template names
        """
        self.template_combo.clear()
        
        self.template_combo.addItems(templates)
    
    def set_source_data(self, headers, data):
        """Set the source data preview.
        
        Args:
            headers: List of column headers
            data: List of rows, each row being a list of values
        """
        self.source_model.clear()
        
        self.source_model.setHorizontalHeaderLabels(headers)
        
        for row in data:
            items = [QStandardItem(str(value)) for value in row]
            self.source_model.appendRow(items)
        
        self.source_table.resizeColumnsToContents()
    
    def set_target_data(self, headers, data):
        """Set the target data preview.
        
        Args:
            headers: List of column headers
            data: List of rows, each row being a list of values
        """
        self.target_model.clear()
        
        self.target_model.setHorizontalHeaderLabels(headers)
        
        for row in data:
            items = [QStandardItem(str(value)) for value in row]
            self.target_model.appendRow(items)
        
        self.target_table.resizeColumnsToContents()
        
        self.convert_button.setEnabled(True)
    
    def set_progress(self, value):
        """Set the progress bar value.
        
        Args:
            value: Progress value (0-100)
        """
        self.progress_bar.setValue(value)
        
        if value >= 100:
            self.progress_bar.setVisible(False)
            self.conversion_completed.emit()
            
            self.preview_button.setEnabled(True)
            self.convert_button.setEnabled(True)
    
    def get_source_format(self):
        """Get the source format.
        
        Returns:
            str: Source format ('csv' or 'qif')
        """
        if self.csv_to_qif_radio.isChecked():
            return 'csv'
        else:
            return 'qif'
    
    def get_target_format(self):
        """Get the target format.
        
        Returns:
            str: Target format ('csv' or 'qif')
        """
        if self.csv_to_qif_radio.isChecked():
            return 'qif'
        else:
            return 'csv'
    
    def get_selected_template(self):
        """Get the selected template.
        
        Returns:
            str: Selected template name
        """
        return self.template_combo.currentText()
    
    def get_selected_account_type(self):
        """Get the selected account type.
        
        Returns:
            str: Selected account type
        """
        return self.account_type_combo.currentText()
