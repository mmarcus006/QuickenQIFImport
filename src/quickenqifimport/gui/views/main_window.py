from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, 
    QWidget, QMenuBar, QMenu, QStatusBar, QToolBar, 
    QAction, QMessageBox, QFileDialog, QLabel
)
from PyQt6.QtCore import Qt, QSettings, pyqtSignal
from PyQt6.QtGui import QIcon, QKeySequence

from .conversion_panel import ConversionPanel
from .template_manager import TemplateManager
from .settings_dialog import SettingsDialog

class MainWindow(QMainWindow):
    """Main application window."""
    
    file_opened = pyqtSignal(str, str)  # file_path, file_type
    conversion_requested = pyqtSignal(str, str)  # source_format, target_format
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        self.settings = QSettings()
        
        self.setWindowTitle("QIF Converter")
        self.setMinimumSize(800, 600)
        
        self.restore_geometry()
        
        self._create_central_widget()
        self._create_menu_bar()
        self._create_tool_bar()
        self._create_status_bar()
        
        self._apply_theme()
    
    def _create_central_widget(self):
        """Create the central widget with tabs."""
        self.tab_widget = QTabWidget()
        
        self.conversion_panel = ConversionPanel()
        self.template_manager = TemplateManager()
        
        self.tab_widget.addTab(self.conversion_panel, "Conversion")
        self.tab_widget.addTab(self.template_manager, "Templates")
        
        self.setCentralWidget(self.tab_widget)
    
    def _create_menu_bar(self):
        """Create the menu bar."""
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu("&File")
        
        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self._on_open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save...", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self._on_save_file)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        edit_menu = menu_bar.addMenu("&Edit")
        
        settings_action = QAction("&Settings...", self)
        settings_action.triggered.connect(self._on_settings)
        edit_menu.addAction(settings_action)
        
        view_menu = menu_bar.addMenu("&View")
        
        theme_action = QAction("Toggle &Theme", self)
        theme_action.triggered.connect(self._toggle_theme)
        view_menu.addAction(theme_action)
        
        help_menu = menu_bar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)
    
    def _create_tool_bar(self):
        """Create the tool bar."""
        tool_bar = self.addToolBar("Main Toolbar")
        tool_bar.setMovable(False)
        
        open_action = QAction("Open", self)
        open_action.triggered.connect(self._on_open_file)
        tool_bar.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.triggered.connect(self._on_save_file)
        tool_bar.addAction(save_action)
        
        tool_bar.addSeparator()
        
        convert_action = QAction("Convert", self)
        convert_action.triggered.connect(self._on_convert)
        tool_bar.addAction(convert_action)
    
    def _create_status_bar(self):
        """Create the status bar."""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        self.status_label = QLabel("Ready")
        status_bar.addWidget(self.status_label)
    
    def _on_open_file(self):
        """Handle open file action."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("All Files (*.*);;CSV Files (*.csv);;QIF Files (*.qif)")
        
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                file_path = file_paths[0]
                
                if file_path.lower().endswith('.csv'):
                    file_type = 'csv'
                elif file_path.lower().endswith('.qif'):
                    file_type = 'qif'
                else:
                    file_type = 'unknown'
                
                self.file_opened.emit(file_path, file_type)
                
                self.status_label.setText(f"Opened: {file_path}")
    
    def _on_save_file(self):
        """Handle save file action."""
        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.setNameFilter("All Files (*.*);;CSV Files (*.csv);;QIF Files (*.qif)")
        
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                file_path = file_paths[0]
                
                if file_path.lower().endswith('.csv'):
                    file_type = 'csv'
                elif file_path.lower().endswith('.qif'):
                    file_type = 'qif'
                else:
                    file_type = 'unknown'
                
                current_tab = self.tab_widget.currentWidget()
                if hasattr(current_tab, 'save_file'):
                    current_tab.save_file(file_path, file_type)
                
                self.status_label.setText(f"Saved: {file_path}")
    
    def _on_convert(self):
        """Handle convert action."""
        current_tab = self.tab_widget.currentWidget()
        
        if current_tab == self.conversion_panel:
            source_format = self.conversion_panel.get_source_format()
            target_format = self.conversion_panel.get_target_format()
            
            if source_format and target_format:
                self.conversion_requested.emit(source_format, target_format)
                
                self.status_label.setText(f"Converting: {source_format} to {target_format}")
    
    def _on_settings(self):
        """Handle settings action."""
        settings_dialog = SettingsDialog(self)
        if settings_dialog.exec():
            self._apply_theme()
    
    def _on_about(self):
        """Handle about action."""
        QMessageBox.about(
            self,
            "About QIF Converter",
            "QIF Converter\n\n"
            "A tool for converting between CSV and QIF formats.\n\n"
            "© 2025 QuickenQIFImport"
        )
    
    def _toggle_theme(self):
        """Toggle between light and dark theme."""
        current_theme = self.settings.value("theme", "light")
        
        new_theme = "dark" if current_theme == "light" else "light"
        
        self.settings.setValue("theme", new_theme)
        
        self._apply_theme()
    
    def _apply_theme(self):
        """Apply the current theme."""
        theme = self.settings.value("theme", "light")
        
        if theme == "dark":
            self.setStyleSheet("""
                QMainWindow, QDialog {
                    background-color: #2d2d2d;
                    color: #ffffff;
                }
                QTabWidget::pane {
                    border: 1px solid #444444;
                    background-color: #2d2d2d;
                }
                QTabBar::tab {
                    background-color: #3d3d3d;
                    color: #ffffff;
                    padding: 8px 16px;
                    border: 1px solid #444444;
                    border-bottom: none;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                QTabBar::tab:selected {
                    background-color: #2d2d2d;
                }
                QMenuBar, QMenu {
                    background-color: #3d3d3d;
                    color: #ffffff;
                }
                QMenuBar::item:selected, QMenu::item:selected {
                    background-color: #555555;
                }
                QToolBar {
                    background-color: #3d3d3d;
                    border: none;
                }
                QStatusBar {
                    background-color: #3d3d3d;
                    color: #ffffff;
                }
                QLabel, QCheckBox, QRadioButton, QGroupBox {
                    color: #ffffff;
                }
                QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox {
                    background-color: #3d3d3d;
                    color: #ffffff;
                    border: 1px solid #555555;
                    padding: 4px;
                }
                QPushButton {
                    background-color: #4d4d4d;
                    color: #ffffff;
                    border: 1px solid #555555;
                    padding: 6px 12px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #555555;
                }
                QPushButton:pressed {
                    background-color: #666666;
                }
                QTableView, QTreeView, QListView {
                    background-color: #3d3d3d;
                    color: #ffffff;
                    border: 1px solid #555555;
                    alternate-background-color: #444444;
                }
                QHeaderView::section {
                    background-color: #4d4d4d;
                    color: #ffffff;
                    padding: 4px;
                    border: 1px solid #555555;
                }
            """)
        else:
            self.setStyleSheet("")
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.save_geometry()
        
        event.accept()
    
    def save_geometry(self):
        """Save window geometry to settings."""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
    
    def restore_geometry(self):
        """Restore window geometry from settings."""
        if self.settings.contains("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))
        if self.settings.contains("windowState"):
            self.restoreState(self.settings.value("windowState"))
    
    def set_status(self, message):
        """Set status bar message."""
        self.status_label.setText(message)
