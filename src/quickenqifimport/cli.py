import argparse
import sys
import os
import json
import logging
from typing import Dict, Any, Optional, List

from .models.models import CSVTemplate, AccountType
from .services.csv_to_qif_service import CSVToQIFService, CSVToQIFServiceError
from .services.qif_to_csv_service import QIFToCSVService, QIFToCSVServiceError
from .utils.template_utils import load_template, list_templates, create_default_templates
from .utils.file_utils import load_yaml

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("qif_converter_cli")

def parse_args():
    """Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Convert between CSV and QIF formats for financial transactions."
    )
    
    parser.add_argument(
        "input_file",
        help="Path to input file (CSV or QIF)"
    )
    
    parser.add_argument(
        "output_file",
        help="Path to output file (QIF or CSV)"
    )
    
    parser.add_argument(
        "--type", "-t",
        choices=["bank", "cash", "credit_card", "investment", "asset", "liability"],
        default="bank",
        help="Transaction type (default: bank)"
    )
    
    parser.add_argument(
        "--template", "-m",
        help="Template name or path to template file"
    )
    
    parser.add_argument(
        "--account", "-a",
        help="Account name to use"
    )
    
    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="List available templates"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--direction",
        choices=["csv2qif", "qif2csv"],
        help="Conversion direction (auto-detected from file extensions if not specified)"
    )
    
    return parser.parse_args()

def detect_file_type(filename: str) -> str:
    """Detect file type based on file extension.
    
    Args:
        filename: Path to the file
        
    Returns:
        str: Detected file type ('csv', 'qif', or 'unknown')
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.csv':
        return 'csv'
    elif ext == '.qif':
        return 'qif'
    else:
        return 'unknown'

def get_account_type(type_str: str) -> AccountType:
    """Convert account type string to AccountType enum.
    
    Args:
        type_str: Account type string
        
    Returns:
        AccountType: Corresponding AccountType enum value
    """
    type_map = {
        "bank": AccountType.BANK,
        "cash": AccountType.CASH,
        "credit_card": AccountType.CREDIT_CARD,
        "investment": AccountType.INVESTMENT,
        "asset": AccountType.ASSET,
        "liability": AccountType.LIABILITY,
    }
    
    return type_map.get(type_str, AccountType.BANK)

def load_template_from_arg(template_arg: str, account_type: AccountType) -> CSVTemplate:
    """Load a template from a name or file path.
    
    Args:
        template_arg: Template name or file path
        account_type: Account type to use if creating a default template
        
    Returns:
        CSVTemplate: Loaded template
        
    Raises:
        ValueError: If the template cannot be loaded
    """
    if os.path.exists(template_arg):
        try:
            template_data = load_yaml(template_arg)
            return CSVTemplate(**template_data)
        except Exception as e:
            raise ValueError(f"Failed to load template from file: {str(e)}")
    
    try:
        return load_template(template_arg)
    except Exception as e:
        logger.warning(f"Template '{template_arg}' not found, using default template for {account_type}")
        
        create_default_templates()
        
        default_template_name = None
        if account_type == AccountType.BANK:
            default_template_name = "generic_bank"
        elif account_type == AccountType.CREDIT_CARD:
            default_template_name = "generic_credit_card"
        elif account_type == AccountType.INVESTMENT:
            default_template_name = "generic_investment"
        
        if default_template_name:
            try:
                return load_template(default_template_name)
            except Exception as e2:
                raise ValueError(f"Failed to load default template: {str(e2)}")
        else:
            raise ValueError(f"No default template available for account type {account_type}")

def convert_csv_to_qif(input_file: str, output_file: str, template: CSVTemplate, account_name: Optional[str] = None):
    """Convert a CSV file to QIF format.
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output QIF file
        template: Template to use for conversion
        account_name: Optional account name to use
    """
    logger.info(f"Converting CSV file '{input_file}' to QIF file '{output_file}'")
    
    service = CSVToQIFService()
    
    try:
        service.convert_csv_file_to_qif_file(input_file, template, output_file, account_name)
        
        logger.info(f"Conversion completed successfully")
    except CSVToQIFServiceError as e:
        logger.error(f"Conversion failed: {str(e)}")
        sys.exit(1)

def convert_qif_to_csv(input_file: str, output_file: str, template: CSVTemplate, account_name: Optional[str] = None):
    """Convert a QIF file to CSV format.
    
    Args:
        input_file: Path to input QIF file
        output_file: Path to output CSV file
        template: Template to use for conversion
        account_name: Optional account name to use
    """
    logger.info(f"Converting QIF file '{input_file}' to CSV file '{output_file}'")
    
    service = QIFToCSVService()
    
    try:
        service.convert_qif_file_to_csv_file(input_file, template, output_file, account_name)
        
        logger.info(f"Conversion completed successfully")
    except QIFToCSVServiceError as e:
        logger.error(f"Conversion failed: {str(e)}")
        sys.exit(1)

def main():
    """Main entry point for the CLI application."""
    args = parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    if args.list_templates:
        templates = list_templates()
        print("Available templates:")
        for template in templates:
            print(f"  - {template}")
        return
    
    if not os.path.exists(args.input_file):
        logger.error(f"Input file '{args.input_file}' does not exist")
        sys.exit(1)
    
    direction = args.direction
    if not direction:
        input_ext = os.path.splitext(args.input_file)[1].lower()
        output_ext = os.path.splitext(args.output_file)[1].lower()
        
        if input_ext == '.csv' and output_ext == '.qif':
            direction = 'csv2qif'
        elif input_ext == '.qif' and output_ext == '.csv':
            direction = 'qif2csv'
        else:
            logger.error(f"Could not determine conversion direction from file extensions")
            logger.error(f"Please specify --direction csv2qif or --direction qif2csv")
            sys.exit(1)
    
    account_type = get_account_type(args.type)
    
    template = None
    if args.template:
        try:
            template = load_template_from_arg(args.template, account_type)
        except ValueError as e:
            logger.error(str(e))
            sys.exit(1)
    else:
        create_default_templates()
        
        default_template_name = None
        if account_type == AccountType.BANK:
            default_template_name = "generic_bank"
        elif account_type == AccountType.CREDIT_CARD:
            default_template_name = "generic_credit_card"
        elif account_type == AccountType.INVESTMENT:
            default_template_name = "generic_investment"
        
        if default_template_name:
            try:
                template = load_template(default_template_name)
                logger.info(f"Using default template '{default_template_name}'")
            except Exception as e:
                logger.error(f"Failed to load default template: {str(e)}")
                sys.exit(1)
        else:
            logger.error(f"No default template available for account type {account_type}")
            sys.exit(1)
    
    if direction == 'csv2qif':
        convert_csv_to_qif(args.input_file, args.output_file, template, args.account)
    else:
        convert_qif_to_csv(args.input_file, args.output_file, template, args.account)

if __name__ == "__main__":
    main()
