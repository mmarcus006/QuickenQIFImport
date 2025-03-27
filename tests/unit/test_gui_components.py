import pytest
from unittest.mock import MagicMock, patch
import sys
import os

from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt6.QtCore import Qt, QTimer

from quickenqifimport.gui.views.main_window import MainWindow
from quickenqifimport.gui.views.conversion_panel import ConversionPanel
from quickenqifimport.gui.views.template_manager import TemplateManager
from quickenqifimport.gui.views.transaction_editor import TransactionEditor
from quickenqifimport.gui.views.settings_dialog import SettingsDialog
from quickenqifimport.gui.controllers.main_controller import MainController
from quickenqifimport.gui.controllers.conversion_controller import ConversionController
from quickenqifimport.gui.controllers.template_controller import TemplateController
from quickenqifimport.gui.controllers.transaction_controller import TransactionController
from quickenqifimport.models.models import CSVTemplate, AccountType, BankingTransaction

class TestMainWindow:
    """Unit tests for the MainWindow class."""
    
    @pytest.fixture
    def app(self):
        """Fixture for QApplication."""
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        yield app
    
    @pytest.fixture
    def main_window(self, app):
        """Fixture for MainWindow."""
        window = MainWindow()
        yield window
        window.close()
    
    @pytest.fixture
    def main_controller(self, main_window):
        """Fixture for MainController."""
        controller = MainController(main_window)
        return controller
    
    def test_main_window_init(self, main_window):
        """Test MainWindow initialization."""
        assert main_window.windowTitle() == "Quicken QIF Import"
        assert main_window.conversion_panel is not None
        assert main_window.template_manager is not None
        assert main_window.menuBar() is not None
    
    def test_main_window_menu_actions(self, main_window):
        """Test MainWindow menu actions."""
        assert main_window.action_open_csv is not None
        assert main_window.action_open_qif is not None
        assert main_window.action_save_as is not None
        assert main_window.action_exit is not None
        assert main_window.action_settings is not None
        assert main_window.action_about is not None
    
    @patch('quickenqifimport.gui.views.main_window.QFileDialog.getOpenFileName')
    def test_open_csv_file(self, mock_file_dialog, main_window, main_controller):
        """Test opening a CSV file."""
        mock_file_dialog.return_value = ("/path/to/test.csv", "CSV Files (*.csv)")
        
        main_controller.open_csv_file = MagicMock()
        
        main_window.action_open_csv.trigger()
        
        main_controller.open_csv_file.assert_called_once_with("/path/to/test.csv")
    
    @patch('quickenqifimport.gui.views.main_window.QFileDialog.getOpenFileName')
    def test_open_qif_file(self, mock_file_dialog, main_window, main_controller):
        """Test opening a QIF file."""
        mock_file_dialog.return_value = ("/path/to/test.qif", "QIF Files (*.qif)")
        
        main_controller.open_qif_file = MagicMock()
        
        main_window.action_open_qif.trigger()
        
        main_controller.open_qif_file.assert_called_once_with("/path/to/test.qif")
    
    @patch('quickenqifimport.gui.views.main_window.QFileDialog.getSaveFileName')
    def test_save_as(self, mock_file_dialog, main_window, main_controller):
        """Test saving a file."""
        mock_file_dialog.return_value = ("/path/to/output.qif", "QIF Files (*.qif)")
        
        main_controller.save_file = MagicMock()
        
        main_window.action_save_as.trigger()
        
        main_controller.save_file.assert_called_once_with("/path/to/output.qif")
    
    def test_show_settings(self, main_window, main_controller):
        """Test showing settings dialog."""
        main_controller.show_settings = MagicMock()
        
        main_window.action_settings.trigger()
        
        main_controller.show_settings.assert_called_once()
    
    def test_show_about(self, main_window, main_controller):
        """Test showing about dialog."""
        main_controller.show_about = MagicMock()
        
        main_window.action_about.trigger()
        
        main_controller.show_about.assert_called_once()

class TestConversionPanel:
    """Unit tests for the ConversionPanel class."""
    
    @pytest.fixture
    def app(self):
        """Fixture for QApplication."""
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        yield app
    
    @pytest.fixture
    def conversion_panel(self, app):
        """Fixture for ConversionPanel."""
        panel = ConversionPanel()
        yield panel
    
    @pytest.fixture
    def conversion_controller(self, conversion_panel):
        """Fixture for ConversionController."""
        controller = ConversionController(conversion_panel)
        return controller
    
    def test_conversion_panel_init(self, conversion_panel):
        """Test ConversionPanel initialization."""
        assert conversion_panel.account_type_combo is not None
        assert conversion_panel.template_combo is not None
        assert conversion_panel.convert_button is not None
        assert conversion_panel.preview_button is not None
    
    def test_set_templates(self, conversion_panel):
        """Test setting templates in the combo box."""
        templates = ["Template 1", "Template 2", "Template 3"]
        conversion_panel.set_templates(templates)
        
        assert conversion_panel.template_combo.count() == 3
        assert conversion_panel.template_combo.itemText(0) == "Template 1"
        assert conversion_panel.template_combo.itemText(1) == "Template 2"
        assert conversion_panel.template_combo.itemText(2) == "Template 3"
    
    def test_set_account_types(self, conversion_panel):
        """Test setting account types in the combo box."""
        account_types = [
            ("Bank", AccountType.BANK),
            ("Cash", AccountType.CASH),
            ("Credit Card", AccountType.CREDIT_CARD),
            ("Investment", AccountType.INVESTMENT)
        ]
        conversion_panel.set_account_types(account_types)
        
        assert conversion_panel.account_type_combo.count() == 4
        assert conversion_panel.account_type_combo.itemText(0) == "Bank"
        assert conversion_panel.account_type_combo.itemText(1) == "Cash"
        assert conversion_panel.account_type_combo.itemText(2) == "Credit Card"
        assert conversion_panel.account_type_combo.itemText(3) == "Investment"
    
    def test_get_selected_template(self, conversion_panel):
        """Test getting the selected template."""
        templates = ["Template 1", "Template 2", "Template 3"]
        conversion_panel.set_templates(templates)
        conversion_panel.template_combo.setCurrentIndex(1)
        
        assert conversion_panel.get_selected_template() == "Template 2"
    
    def test_get_selected_account_type(self, conversion_panel):
        """Test getting the selected account type."""
        account_types = [
            ("Bank", AccountType.BANK),
            ("Cash", AccountType.CASH),
            ("Credit Card", AccountType.CREDIT_CARD),
            ("Investment", AccountType.INVESTMENT)
        ]
        conversion_panel.set_account_types(account_types)
        conversion_panel.account_type_combo.setCurrentIndex(2)
        
        assert conversion_panel.get_selected_account_type() == AccountType.CREDIT_CARD
    
    def test_convert_button_clicked(self, conversion_panel, conversion_controller):
        """Test convert button click."""
        conversion_controller.convert = MagicMock()
        
        conversion_panel.convert_button.click()
        
        conversion_controller.convert.assert_called_once()
    
    def test_preview_button_clicked(self, conversion_panel, conversion_controller):
        """Test preview button click."""
        conversion_controller.preview = MagicMock()
        
        conversion_panel.preview_button.click()
        
        conversion_controller.preview.assert_called_once()

class TestTemplateManager:
    """Unit tests for the TemplateManager class."""
    
    @pytest.fixture
    def app(self):
        """Fixture for QApplication."""
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        yield app
    
    @pytest.fixture
    def template_manager(self, app):
        """Fixture for TemplateManager."""
        manager = TemplateManager()
        yield manager
    
    @pytest.fixture
    def template_controller(self, template_manager):
        """Fixture for TemplateController."""
        controller = TemplateController(template_manager)
        return controller
    
    def test_template_manager_init(self, template_manager):
        """Test TemplateManager initialization."""
        assert template_manager.template_list is not None
        assert template_manager.new_button is not None
        assert template_manager.edit_button is not None
        assert template_manager.delete_button is not None
        assert template_manager.import_button is not None
        assert template_manager.export_button is not None
    
    def test_set_templates(self, template_manager):
        """Test setting templates in the list widget."""
        templates = ["Template 1", "Template 2", "Template 3"]
        template_manager.set_templates(templates)
        
        assert template_manager.template_list.count() == 3
        assert template_manager.template_list.item(0).text() == "Template 1"
        assert template_manager.template_list.item(1).text() == "Template 2"
        assert template_manager.template_list.item(2).text() == "Template 3"
    
    def test_get_selected_template(self, template_manager):
        """Test getting the selected template."""
        templates = ["Template 1", "Template 2", "Template 3"]
        template_manager.set_templates(templates)
        template_manager.template_list.setCurrentRow(1)
        
        assert template_manager.get_selected_template() == "Template 2"
    
    def test_new_button_clicked(self, template_manager, template_controller):
        """Test new button click."""
        template_controller.create_template = MagicMock()
        
        template_manager.new_button.click()
        
        template_controller.create_template.assert_called_once()
    
    def test_edit_button_clicked(self, template_manager, template_controller):
        """Test edit button click."""
        templates = ["Template 1", "Template 2", "Template 3"]
        template_manager.set_templates(templates)
        template_manager.template_list.setCurrentRow(1)
        
        template_controller.edit_template = MagicMock()
        
        template_manager.edit_button.click()
        
        template_controller.edit_template.assert_called_once_with("Template 2")
    
    def test_delete_button_clicked(self, template_manager, template_controller):
        """Test delete button click."""
        templates = ["Template 1", "Template 2", "Template 3"]
        template_manager.set_templates(templates)
        template_manager.template_list.setCurrentRow(1)
        
        template_controller.delete_template = MagicMock()
        
        template_manager.delete_button.click()
        
        template_controller.delete_template.assert_called_once_with("Template 2")
