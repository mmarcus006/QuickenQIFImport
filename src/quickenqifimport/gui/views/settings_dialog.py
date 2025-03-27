from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QPushButton, QComboBox, QLineEdit, QCheckBox, QSpinBox,
    QTabWidget, QWidget, QGroupBox, QRadioButton, QDialogButtonBox,
    QColorDialog, QFontDialog, QFileDialog
)
from PyQt6.QtCore import Qt, QSettings, pyqtSignal
from PyQt6.QtGui import QFont

class SettingsDialog(QDialog):
    """Dialog for application settings."""
    
    settings_saved = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the settings dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.settings = QSettings()
        
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        
        self._create_ui()
        
        self._load_settings()
    
    def _create_ui(self):
        """Create the UI components."""
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        general_tab = self._create_general_tab()
        appearance_tab = self._create_appearance_tab()
        advanced_tab = self._create_advanced_tab()
        
        tab_widget.addTab(general_tab, "General")
        tab_widget.addTab(appearance_tab, "Appearance")
        tab_widget.addTab(advanced_tab, "Advanced")
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        main_layout.addWidget(button_box)
        
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
    
    def _create_general_tab(self):
        """Create the general settings tab.
        
        Returns:
            QWidget: General settings tab
        """
        tab = QWidget()
        layout = QFormLayout()
        tab.setLayout(layout)
        
        self.default_template_combo = QComboBox()
        self.auto_save_check = QCheckBox("Auto-save converted files")
        self.remember_paths_check = QCheckBox("Remember last used paths")
        self.confirm_overwrite_check = QCheckBox("Confirm before overwriting files")
        
        layout.addRow("Default Template:", self.default_template_combo)
        layout.addRow("", self.auto_save_check)
        layout.addRow("", self.remember_paths_check)
        layout.addRow("", self.confirm_overwrite_check)
        
        return tab
    
    def _create_appearance_tab(self):
        """Create the appearance settings tab.
        
        Returns:
            QWidget: Appearance settings tab
        """
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout()
        theme_group.setLayout(theme_layout)
        
        self.light_theme_radio = QRadioButton("Light Theme")
        self.dark_theme_radio = QRadioButton("Dark Theme")
        self.system_theme_radio = QRadioButton("Use System Theme")
        
        theme_layout.addWidget(self.light_theme_radio)
        theme_layout.addWidget(self.dark_theme_radio)
        theme_layout.addWidget(self.system_theme_radio)
        
        font_group = QGroupBox("Font")
        font_layout = QHBoxLayout()
        font_group.setLayout(font_layout)
        
        self.font_label = QLabel("Current Font: Default")
        self.font_button = QPushButton("Change Font...")
        
        font_layout.addWidget(self.font_label)
        font_layout.addWidget(self.font_button)
        
        accessibility_group = QGroupBox("Accessibility")
        accessibility_layout = QVBoxLayout()
        accessibility_group.setLayout(accessibility_layout)
        
        self.high_contrast_check = QCheckBox("High Contrast Mode")
        self.large_text_check = QCheckBox("Large Text")
        self.screen_reader_check = QCheckBox("Screen Reader Support")
        
        accessibility_layout.addWidget(self.high_contrast_check)
        accessibility_layout.addWidget(self.large_text_check)
        accessibility_layout.addWidget(self.screen_reader_check)
        
        layout.addWidget(theme_group)
        layout.addWidget(font_group)
        layout.addWidget(accessibility_group)
        
        self.font_button.clicked.connect(self._on_change_font)
        
        return tab
    
    def _create_advanced_tab(self):
        """Create the advanced settings tab.
        
        Returns:
            QWidget: Advanced settings tab
        """
        tab = QWidget()
        layout = QFormLayout()
        tab.setLayout(layout)
        
        self.templates_dir_edit = QLineEdit()
        self.templates_dir_edit.setReadOnly(True)
        templates_dir_button = QPushButton("Browse...")
        templates_dir_layout = QHBoxLayout()
        templates_dir_layout.addWidget(self.templates_dir_edit)
        templates_dir_layout.addWidget(templates_dir_button)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["Debug", "Info", "Warning", "Error"])
        
        self.max_preview_rows_spin = QSpinBox()
        self.max_preview_rows_spin.setMinimum(10)
        self.max_preview_rows_spin.setMaximum(1000)
        self.max_preview_rows_spin.setSingleStep(10)
        
        layout.addRow("Templates Directory:", templates_dir_layout)
        layout.addRow("Log Level:", self.log_level_combo)
        layout.addRow("Max Preview Rows:", self.max_preview_rows_spin)
        
        templates_dir_button.clicked.connect(self._on_browse_templates_dir)
        
        return tab
    
    def _load_settings(self):
        """Load current settings."""
        self.auto_save_check.setChecked(self.settings.value("auto_save", False, type=bool))
        self.remember_paths_check.setChecked(self.settings.value("remember_paths", True, type=bool))
        self.confirm_overwrite_check.setChecked(self.settings.value("confirm_overwrite", True, type=bool))
        
        theme = self.settings.value("theme", "light")
        if theme == "light":
            self.light_theme_radio.setChecked(True)
        elif theme == "dark":
            self.dark_theme_radio.setChecked(True)
        else:
            self.system_theme_radio.setChecked(True)
        
        font_family = self.settings.value("font_family", "")
        font_size = self.settings.value("font_size", 0, type=int)
        if font_family and font_size > 0:
            self.font_label.setText(f"Current Font: {font_family}, {font_size}pt")
        
        self.high_contrast_check.setChecked(self.settings.value("high_contrast", False, type=bool))
        self.large_text_check.setChecked(self.settings.value("large_text", False, type=bool))
        self.screen_reader_check.setChecked(self.settings.value("screen_reader", False, type=bool))
        
        self.templates_dir_edit.setText(self.settings.value("templates_dir", ""))
        
        log_level = self.settings.value("log_level", "Info")
        log_level_index = self.log_level_combo.findText(log_level)
        if log_level_index >= 0:
            self.log_level_combo.setCurrentIndex(log_level_index)
        
        self.max_preview_rows_spin.setValue(self.settings.value("max_preview_rows", 100, type=int))
    
    def _save_settings(self):
        """Save current settings."""
        self.settings.setValue("auto_save", self.auto_save_check.isChecked())
        self.settings.setValue("remember_paths", self.remember_paths_check.isChecked())
        self.settings.setValue("confirm_overwrite", self.confirm_overwrite_check.isChecked())
        
        if self.light_theme_radio.isChecked():
            self.settings.setValue("theme", "light")
        elif self.dark_theme_radio.isChecked():
            self.settings.setValue("theme", "dark")
        else:
            self.settings.setValue("theme", "system")
        
        self.settings.setValue("high_contrast", self.high_contrast_check.isChecked())
        self.settings.setValue("large_text", self.large_text_check.isChecked())
        self.settings.setValue("screen_reader", self.screen_reader_check.isChecked())
        
        self.settings.setValue("templates_dir", self.templates_dir_edit.text())
        self.settings.setValue("log_level", self.log_level_combo.currentText())
        self.settings.setValue("max_preview_rows", self.max_preview_rows_spin.value())
    
    def _on_change_font(self):
        """Handle change font button click event."""
        current_font = QFont()
        font_family = self.settings.value("font_family", "")
        font_size = self.settings.value("font_size", 0, type=int)
        
        if font_family and font_size > 0:
            current_font.setFamily(font_family)
            current_font.setPointSize(font_size)
        
        font, ok = QFontDialog.getFont(current_font, self)
        
        if ok:
            self.settings.setValue("font_family", font.family())
            self.settings.setValue("font_size", font.pointSize())
            
            self.font_label.setText(f"Current Font: {font.family()}, {font.pointSize()}pt")
    
    def _on_browse_templates_dir(self):
        """Handle browse templates directory button click event."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Templates Directory",
            self.templates_dir_edit.text()
        )
        
        if directory:
            self.templates_dir_edit.setText(directory)
    
    def _on_accept(self):
        """Handle accept button click event."""
        self._save_settings()
        
        self.settings_saved.emit()
        
        self.accept()
    
    def set_templates(self, templates):
        """Set the available templates.
        
        Args:
            templates: List of template names
        """
        self.default_template_combo.clear()
        
        self.default_template_combo.addItems(templates)
        
        default_template = self.settings.value("default_template", "")
        if default_template:
            index = self.default_template_combo.findText(default_template)
            if index >= 0:
                self.default_template_combo.setCurrentIndex(index)
