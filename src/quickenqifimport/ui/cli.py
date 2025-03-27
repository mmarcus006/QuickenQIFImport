import argparse
import os
import sys
from typing import List, Optional

from ..models.qif_models import QIFAccountType
from ..parsers.qif_parser import QIFParser
from ..parsers.csv_parser import CSVParser
from ..converters.qif_to_csv_converter import QIFToCSVConverter
from ..converters.csv_to_qif_converter import CSVToQIFConverter
from ..models.csv_models import CSVTemplate


class CLI:
    """Command Line Interface for the QuickenQIFImport application."""
    
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Convert between QIF and CSV formats for financial data."
        )
        self._setup_arguments()
        
    def _setup_arguments(self):
        """Set up command line arguments."""
        subparsers = self.parser.add_subparsers(dest="command", help="Command to execute")
        
        qif_to_csv_parser = subparsers.add_parser("qif2csv", help="Convert QIF to CSV")
        qif_to_csv_parser.add_argument("input", help="Input QIF file path")
        qif_to_csv_parser.add_argument("output", help="Output CSV file path")
        qif_to_csv_parser.add_argument("--template", help="Template file path")
        qif_to_csv_parser.add_argument("--date-format", default="%Y-%m-%d", help="Date format for output")
        qif_to_csv_parser.add_argument("--delimiter", default=",", help="CSV delimiter")
        
        csv_to_qif_parser = subparsers.add_parser("csv2qif", help="Convert CSV to QIF")
        csv_to_qif_parser.add_argument("input", help="Input CSV file path")
        csv_to_qif_parser.add_argument("output", help="Output QIF file path")
        csv_to_qif_parser.add_argument("--type", choices=[t.value for t in QIFAccountType], 
                                      default="Bank", help="QIF account type")
        csv_to_qif_parser.add_argument("--template", help="Template file path")
        csv_to_qif_parser.add_argument("--date-format", default="%Y-%m-%d", help="Date format for input")
        
        template_parser = subparsers.add_parser("template", help="Template management")
        template_subparsers = template_parser.add_subparsers(dest="template_command", help="Template command")
        
        create_template_parser = template_subparsers.add_parser("create", help="Create a new template")
        create_template_parser.add_argument("name", help="Template name")
        create_template_parser.add_argument("output", help="Output template file path")
        create_template_parser.add_argument("--type", choices=[t.value for t in QIFAccountType], 
                                          default="Bank", help="QIF account type")
        create_template_parser.add_argument("--description", help="Template description")
        create_template_parser.add_argument("--date-format", default="%Y-%m-%d", help="Date format")
        create_template_parser.add_argument("--delimiter", default=",", help="CSV delimiter")
        
        list_template_parser = template_subparsers.add_parser("list", help="List available templates")
        list_template_parser.add_argument("directory", help="Templates directory")
        
        view_template_parser = template_subparsers.add_parser("view", help="View template details")
        view_template_parser.add_argument("template", help="Template file path")
        
    def run(self, args: Optional[List[str]] = None) -> int:
        """Run the CLI with the provided arguments."""
        parsed_args = self.parser.parse_args(args)
        
        if not parsed_args.command:
            self.parser.print_help()
            return 1
            
        try:
            if parsed_args.command == "qif2csv":
                return self._handle_qif_to_csv(parsed_args)
            elif parsed_args.command == "csv2qif":
                return self._handle_csv_to_qif(parsed_args)
            elif parsed_args.command == "template":
                return self._handle_template(parsed_args)
            else:
                print(f"Unknown command: {parsed_args.command}")
                return 1
        except Exception as e:
            print(f"Error: {e}")
            return 1
            
    def _handle_qif_to_csv(self, args) -> int:
        """Handle QIF to CSV conversion."""
        if not os.path.isfile(args.input):
            print(f"Input file not found: {args.input}")
            return 1
            
        template = None
        if args.template:
            if not os.path.isfile(args.template):
                print(f"Template file not found: {args.template}")
                return 1
                
            
        converter = QIFToCSVConverter(date_format=args.date_format, delimiter=args.delimiter)
        try:
            converter.convert_file(args.input, args.output, template)
            print(f"Successfully converted {args.input} to {args.output}")
            return 0
        except Exception as e:
            print(f"Conversion failed: {e}")
            return 1
            
    def _handle_csv_to_qif(self, args) -> int:
        """Handle CSV to QIF conversion."""
        if not os.path.isfile(args.input):
            print(f"Input file not found: {args.input}")
            return 1
            
        template = None
        if args.template:
            if not os.path.isfile(args.template):
                print(f"Template file not found: {args.template}")
                return 1
                
            
        account_type = QIFAccountType(args.type)
        converter = CSVToQIFConverter(date_format=args.date_format)
        try:
            converter.convert_file(args.input, args.output, account_type, template)
            print(f"Successfully converted {args.input} to {args.output}")
            return 0
        except Exception as e:
            print(f"Conversion failed: {e}")
            return 1
            
    def _handle_template(self, args) -> int:
        """Handle template management."""
        if not args.template_command:
            print("No template command specified")
            return 1
            
        if args.template_command == "create":
            return self._handle_create_template(args)
        elif args.template_command == "list":
            return self._handle_list_templates(args)
        elif args.template_command == "view":
            return self._handle_view_template(args)
        else:
            print(f"Unknown template command: {args.template_command}")
            return 1
            
    def _handle_create_template(self, args) -> int:
        """Handle template creation."""
        print(f"Creating template {args.name} at {args.output}")
        return 0
        
    def _handle_list_templates(self, args) -> int:
        """Handle template listing."""
        if not os.path.isdir(args.directory):
            print(f"Directory not found: {args.directory}")
            return 1
            
        template_files = [f for f in os.listdir(args.directory) if f.endswith('.json')]
        if not template_files:
            print(f"No templates found in {args.directory}")
            return 0
            
        print(f"Templates in {args.directory}:")
        for template_file in template_files:
            print(f"  - {template_file}")
            
        return 0
        
    def _handle_view_template(self, args) -> int:
        """Handle template viewing."""
        if not os.path.isfile(args.template):
            print(f"Template file not found: {args.template}")
            return 1
            
        print(f"Template details for {args.template}:")
        return 0


def main():
    """Main entry point for the CLI."""
    cli = CLI()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()
