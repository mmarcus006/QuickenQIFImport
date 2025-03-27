from typing import Dict, Any, List, Optional, Union
import os
import json

from ..models.csv_models import CSVTemplate
from ..utils.file_utils import FileUtils


class TemplateManager:
    """Manager for CSV templates."""
    
    def __init__(self, templates_dir: str = None):
        """
        Initialize the template manager.
        
        Args:
            templates_dir: Directory to store templates
        """
        self.templates_dir = templates_dir
    
    def create_template(self, name: str, account_type: str, field_mapping: Dict[str, str],
                       description: Optional[str] = None, date_format: str = "%Y-%m-%d",
                       delimiter: str = ",") -> CSVTemplate:
        """
        Create a new template.
        
        Args:
            name: Template name
            account_type: Account type
            field_mapping: Field mapping from CSV to QIF
            description: Template description
            date_format: Date format
            delimiter: CSV delimiter
            
        Returns:
            CSVTemplate: The created template
            
        Raises:
            ValueError: If the template name is invalid or already exists
        """
        if not name:
            raise ValueError("Template name cannot be empty")
            
        template = CSVTemplate(
            name=name,
            description=description,
            account_type=account_type,
            field_mapping=field_mapping,
            date_format=date_format,
            delimiter=delimiter
        )
        
        return template
    
    def save_template(self, template: CSVTemplate, file_path: Optional[str] = None) -> str:
        """
        Save a template to a file.
        
        Args:
            template: The template to save
            file_path: Path to save the template, if None, uses templates_dir/name.json
            
        Returns:
            str: The path where the template was saved
            
        Raises:
            ValueError: If the template name is invalid or the templates_dir is not set
            OSError: If the file cannot be written
        """
        if not file_path:
            if not self.templates_dir:
                raise ValueError("Templates directory not set")
                
            FileUtils.ensure_directory_exists(self.templates_dir)
            
            file_path = os.path.join(self.templates_dir, f"{template.name}.json")
            
        FileUtils.save_template(template, file_path)
        
        return file_path
    
    def load_template(self, file_path: str) -> CSVTemplate:
        """
        Load a template from a file.
        
        Args:
            file_path: Path to the template file
            
        Returns:
            CSVTemplate: The loaded template
            
        Raises:
            FileNotFoundError: If the file does not exist
            json.JSONDecodeError: If the file is not valid JSON
            ValueError: If the JSON does not represent a valid template
        """
        return FileUtils.load_template(file_path)
    
    def list_templates(self, directory: Optional[str] = None) -> List[str]:
        """
        List all template files in a directory.
        
        Args:
            directory: Directory to list templates from, if None, uses templates_dir
            
        Returns:
            List[str]: List of template file names
            
        Raises:
            ValueError: If the directory is not set
            FileNotFoundError: If the directory does not exist
        """
        if not directory:
            if not self.templates_dir:
                raise ValueError("Templates directory not set")
                
            directory = self.templates_dir
            
        return FileUtils.list_templates(directory)
    
    def get_template_path(self, template_name: str) -> str:
        """
        Get the path to a template file.
        
        Args:
            template_name: Name of the template
            
        Returns:
            str: Path to the template file
            
        Raises:
            ValueError: If the templates_dir is not set
            FileNotFoundError: If the template does not exist
        """
        if not self.templates_dir:
            raise ValueError("Templates directory not set")
            
        if not template_name.endswith('.json'):
            template_name = f"{template_name}.json"
            
        template_path = os.path.join(self.templates_dir, template_name)
        
        if not os.path.isfile(template_path):
            raise FileNotFoundError(f"Template not found: {template_name}")
            
        return template_path
    
    def delete_template(self, template_name: str) -> None:
        """
        Delete a template.
        
        Args:
            template_name: Name of the template
            
        Raises:
            ValueError: If the templates_dir is not set
            FileNotFoundError: If the template does not exist
            OSError: If the file cannot be deleted
        """
        template_path = self.get_template_path(template_name)
        
        os.remove(template_path)
    
    def create_default_templates(self) -> List[str]:
        """
        Create default templates for common account types.
        
        Returns:
            List[str]: List of created template file paths
            
        Raises:
            ValueError: If the templates_dir is not set
            OSError: If the files cannot be written
        """
        if not self.templates_dir:
            raise ValueError("Templates directory not set")
            
        FileUtils.ensure_directory_exists(self.templates_dir)
        
        templates = []
        
        bank_template = self.create_template(
            name="Bank",
            account_type="Bank",
            field_mapping={
                "Date": "date",
                "Amount": "amount",
                "Description": "payee",
                "Reference": "number",
                "Memo": "memo",
                "Category": "category",
                "Account Name": "account",
                "Status": "cleared_status"
            },
            description="Default template for bank transactions"
        )
        
        bank_path = self.save_template(bank_template)
        templates.append(bank_path)
        
        credit_card_template = self.create_template(
            name="Credit Card",
            account_type="CCard",
            field_mapping={
                "Date": "date",
                "Amount": "amount",
                "Description": "payee",
                "Reference": "number",
                "Memo": "memo",
                "Category": "category",
                "Status": "cleared_status"
            },
            description="Default template for credit card transactions"
        )
        
        credit_card_path = self.save_template(credit_card_template)
        templates.append(credit_card_path)
        
        investment_template = self.create_template(
            name="Investment",
            account_type="Invst",
            field_mapping={
                "Date": "date",
                "Action": "action",
                "Security": "security",
                "Quantity": "quantity",
                "Price": "price",
                "Amount": "amount",
                "Commission": "commission",
                "Description": "text",
                "Memo": "memo",
                "Account": "account",
                "Status": "cleared_status"
            },
            description="Default template for investment transactions"
        )
        
        investment_path = self.save_template(investment_template)
        templates.append(investment_path)
        
        return templates
