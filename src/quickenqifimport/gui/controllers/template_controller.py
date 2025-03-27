from PyQt6.QtWidgets import QMessageBox, QFileDialog
from PyQt6.QtCore import QObject, pyqtSlot
import os
import yaml

from ..views.template_manager import TemplateManager
from ...utils.template_utils import list_templates, load_template, save_template, delete_template
from ...utils.file_utils import load_yaml, save_yaml
from ...models.models import CSVTemplate

class TemplateController(QObject):
    """Controller for the template manager."""
    
    def __init__(self, view: TemplateManager):
        """Initialize the template controller.
        
        Args:
            view: Template manager view
        """
        super().__init__()
        
        self.view = view
        
        self.templates = {}
        
        self._connect_signals()
        
        self._load_templates()
    
    def _connect_signals(self):
        """Connect signals to slots."""
        self.view.template_selected.connect(self._on_template_selected)
        self.view.template_created.connect(self._on_template_created)
        self.view.template_updated.connect(self._on_template_updated)
        self.view.template_deleted.connect(self._on_template_deleted)
    
    def _load_templates(self):
        """Load available templates."""
        try:
            template_names = list_templates()
            
            self.templates = {}
            for name in template_names:
                try:
                    template = load_template(name)
                    self.templates[name] = template
                except Exception as e:
                    print(f"Failed to load template '{name}': {str(e)}")
            
            self.view.set_templates(self.templates)
        except Exception as e:
            self._show_error("Failed to load templates", str(e))
    
    @pyqtSlot(str)
    def _on_template_selected(self, template_name: str):
        """Handle template selected signal.
        
        Args:
            template_name: Name of the selected template
        """
        try:
            template = self.templates.get(template_name)
            
            if template:
                self.view.set_template(template)
            else:
                self._show_error("Template not found", f"Template '{template_name}' not found.")
        except Exception as e:
            self._show_error("Failed to load template", str(e))
    
    @pyqtSlot(CSVTemplate)
    def _on_template_created(self, template: CSVTemplate):
        """Handle template created signal.
        
        Args:
            template: Created template
        """
        try:
            if template.name in self.templates:
                self._show_error(
                    "Template already exists",
                    f"A template with the name '{template.name}' already exists."
                )
                return
            
            save_template(template)
            
            self.templates[template.name] = template
            
            self._load_templates()
            
            self._show_info(
                "Template created",
                f"Template '{template.name}' has been created."
            )
        except Exception as e:
            self._show_error("Failed to create template", str(e))
    
    @pyqtSlot(CSVTemplate)
    def _on_template_updated(self, template: CSVTemplate):
        """Handle template updated signal.
        
        Args:
            template: Updated template
        """
        try:
            save_template(template)
            
            self.templates[template.name] = template
            
            self._load_templates()
            
            self._show_info(
                "Template updated",
                f"Template '{template.name}' has been updated."
            )
        except Exception as e:
            self._show_error("Failed to update template", str(e))
    
    @pyqtSlot(str)
    def _on_template_deleted(self, template_name: str):
        """Handle template deleted signal.
        
        Args:
            template_name: Name of the deleted template
        """
        try:
            delete_template(template_name)
            
            if template_name in self.templates:
                del self.templates[template_name]
            
            self._load_templates()
            
            self._show_info(
                "Template deleted",
                f"Template '{template_name}' has been deleted."
            )
        except Exception as e:
            self._show_error("Failed to delete template", str(e))
    
    def open_file(self, file_path: str):
        """Open a template file.
        
        Args:
            file_path: Path to the template file
        """
        try:
            template_data = load_yaml(file_path)
            template = CSVTemplate(**template_data)
            
            self.view.set_template(template)
            
            self._show_info(
                "Template loaded",
                f"Template '{template.name}' has been loaded from file."
            )
        except Exception as e:
            self._show_error("Failed to load template file", str(e))
    
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
