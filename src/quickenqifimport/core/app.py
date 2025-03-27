from typing import Dict, Any, List, Optional, Union
import os
import sys
import argparse

from ..models.qif_models import QIFAccountType
from ..models.csv_models import CSVTemplate
from .converter import Converter
from .template_manager import TemplateManager
from ..ui.cli import CLI
from ..ui.gui import GUI


class App:
    """Main application class."""
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the application.
        
        Args:
            templates_dir: Directory to store templates
        """
        if not templates_dir:
            home_dir = os.path.expanduser("~")
            templates_dir = os.path.join(home_dir, ".quickenqifimport", "templates")
            
        self.templates_dir = templates_dir
        self.converter = Converter()
        self.template_manager = TemplateManager(templates_dir)
        
        os.makedirs(templates_dir, exist_ok=True)
    
    def run_cli(self, args: Optional[List[str]] = None) -> int:
        """
        Run the command-line interface.
        
        Args:
            args: Command-line arguments
            
        Returns:
            int: Exit code
        """
        cli = CLI()
        return cli.run(args)
    
    def run_gui(self) -> None:
        """Run the graphical user interface."""
        gui = GUI()
        gui.mainloop()
    
    def convert_qif_to_csv(self, qif_file_path: str, csv_file_path: str, 
                          template_path: Optional[str] = None,
                          date_format: str = "%Y-%m-%d",
                          delimiter: str = ",") -> None:
        """
        Convert a QIF file to a CSV file.
        
        Args:
            qif_file_path: Path to the QIF file
            csv_file_path: Path to save the CSV file
            template_path: Path to the template file
            date_format: Date format for the CSV file
            delimiter: Delimiter for the CSV file
            
        Raises:
            FileNotFoundError: If the QIF file or template file does not exist
            ValueError: If the QIF file is invalid
            OSError: If the CSV file cannot be written
        """
        template = None
        if template_path:
            template = self.template_manager.load_template(template_path)
            
        self.converter.convert_qif_to_csv(qif_file_path, csv_file_path, template, date_format, delimiter)
    
    def convert_csv_to_qif(self, csv_file_path: str, qif_file_path: str, 
                          account_type: Union[QIFAccountType, str],
                          template_path: Optional[str] = None,
                          date_format: str = "%Y-%m-%d") -> None:
        """
        Convert a CSV file to a QIF file.
        
        Args:
            csv_file_path: Path to the CSV file
            qif_file_path: Path to save the QIF file
            account_type: QIF account type
            template_path: Path to the template file
            date_format: Date format for the CSV file
            
        Raises:
            FileNotFoundError: If the CSV file or template file does not exist
            ValueError: If the CSV file is invalid or the account type is invalid
            OSError: If the QIF file cannot be written
        """
        template = None
        if template_path:
            template = self.template_manager.load_template(template_path)
            
        self.converter.convert_csv_to_qif(csv_file_path, qif_file_path, account_type, template, date_format)
    
    def create_template(self, name: str, account_type: str, field_mapping: Dict[str, str],
                       description: Optional[str] = None, date_format: str = "%Y-%m-%d",
                       delimiter: str = ",", save: bool = True) -> CSVTemplate:
        """
        Create a new template.
        
        Args:
            name: Template name
            account_type: Account type
            field_mapping: Field mapping from CSV to QIF
            description: Template description
            date_format: Date format
            delimiter: CSV delimiter
            save: Whether to save the template
            
        Returns:
            CSVTemplate: The created template
            
        Raises:
            ValueError: If the template name is invalid or already exists
            OSError: If the template cannot be saved
        """
        template = self.template_manager.create_template(
            name=name,
            account_type=account_type,
            field_mapping=field_mapping,
            description=description,
            date_format=date_format,
            delimiter=delimiter
        )
        
        if save:
            self.template_manager.save_template(template)
            
        return template
    
    def create_default_templates(self) -> List[str]:
        """
        Create default templates for common account types.
        
        Returns:
            List[str]: List of created template file paths
            
        Raises:
            OSError: If the templates cannot be created
        """
        return self.template_manager.create_default_templates()


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="QuickenQIFImport - Convert between QIF and CSV formats")
    parser.add_argument("--gui", action="store_true", help="Start the graphical user interface")
    parser.add_argument("--templates-dir", help="Directory to store templates")
    
    args, remaining_args = parser.parse_known_args()
    
    app = App(templates_dir=args.templates_dir)
    
    if args.gui:
        app.run_gui()
    else:
        sys.exit(app.run_cli(remaining_args))


if __name__ == "__main__":
    main()
