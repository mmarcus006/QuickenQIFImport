from typing import Dict, List, Optional, Union, Any
import os

from ..models.models import (
    QIFFile, BaseTransaction, BankingTransaction, InvestmentTransaction,
    CSVTemplate, AccountDefinition, AccountType
)
from ..parsers.csv_parser import CSVParser, CSVParserError
from ..generators.qif_generator import QIFGenerator, QIFGeneratorError
from ..validators.csv_validator import CSVValidator, CSVValidationError
from ..validators.template_validator import TemplateValidator, TemplateValidationError
from ..services.transfer_recognition_service import TransferRecognitionService

class CSVToQIFServiceError(Exception):
    """Exception raised for errors during CSV to QIF conversion."""
    pass

class CSVToQIFService:
    """Service for converting CSV data to QIF format."""
    
    def __init__(self):
        """Initialize the CSV to QIF conversion service."""
        self.csv_parser = CSVParser()
        self.qif_generator = QIFGenerator()
        self.csv_validator = CSVValidator()
        self.template_validator = TemplateValidator()
        self.transfer_service = TransferRecognitionService()
    
    def convert_csv_to_qif(self, csv_content: str, template: CSVTemplate, 
                          account_name: Optional[str] = None) -> str:
        """Convert CSV content to QIF format using the provided template.
        
        Args:
            csv_content: String containing CSV data
            template: CSVTemplate defining the mapping between CSV columns and transaction fields
            account_name: Optional account name to use (defaults to template name if not provided)
            
        Returns:
            str: Generated QIF content
            
        Raises:
            CSVToQIFServiceError: If the conversion fails
        """
        try:
            template_valid, template_errors = self.template_validator.validate_template(template)
            if not template_valid:
                error_messages = [str(err) for err in template_errors]
                raise CSVToQIFServiceError(
                    f"Invalid template: {'; '.join(error_messages)}"
                )
            
            csv_valid, csv_errors = self.csv_validator.validate_csv_format(
                csv_content, template.delimiter, template.has_header
            )
            if not csv_valid:
                filtered_errors = [err for err in csv_errors if "Empty column value" not in str(err)]
                if not filtered_errors:
                    csv_valid = True
                else:
                    error_messages = [str(err) for err in filtered_errors]
                    raise CSVToQIFServiceError(
                        f"Invalid CSV format: {'; '.join(error_messages)}"
                    )
            
            data_valid, data_errors = self.csv_validator.validate_csv_data(csv_content, template)
            if not data_valid:
                error_messages = [str(err) for err in data_errors]
                raise CSVToQIFServiceError(
                    f"Invalid CSV data: {'; '.join(error_messages)}"
                )
            
            transactions = self.csv_parser.parse_csv(csv_content, template)
            
            if template.detect_transfers:
                transactions = self.transfer_service.process_transfers(transactions)
            
            qif_file = QIFFile()
            
            account_name = account_name or template.name
            
            account = AccountDefinition(
                name=account_name,
                type=template.account_type,
                description=template.description
            )
            qif_file.accounts.append(account)
            
            if template.account_type == AccountType.INVESTMENT:
                qif_file.investment_transactions[account_name] = transactions
            elif template.account_type == AccountType.BANK:
                qif_file.bank_transactions[account_name] = transactions
            elif template.account_type == AccountType.CASH:
                qif_file.cash_transactions[account_name] = transactions
            elif template.account_type == AccountType.CREDIT_CARD:
                qif_file.credit_card_transactions[account_name] = transactions
            elif template.account_type == AccountType.ASSET:
                qif_file.asset_transactions[account_name] = transactions
            elif template.account_type == AccountType.LIABILITY:
                qif_file.liability_transactions[account_name] = transactions
            
            qif_content = self.qif_generator.generate_qif_file(qif_file)
            
            return qif_content
            
        except Exception as e:
            if isinstance(e, CSVToQIFServiceError):
                raise
            raise CSVToQIFServiceError(f"Failed to convert CSV to QIF: {str(e)}")
    
    def convert_csv_file_to_qif_file(self, csv_file_path: str, template: CSVTemplate,
                                   qif_file_path: Optional[str] = None,
                                   account_name: Optional[str] = None) -> str:
        """Convert a CSV file to a QIF file using the provided template.
        
        Args:
            csv_file_path: Path to the CSV file
            template: CSVTemplate defining the mapping between CSV columns and transaction fields
            qif_file_path: Optional path to save the QIF file (if not provided, will use the same
                          name as the CSV file with .qif extension)
            account_name: Optional account name to use (defaults to template name if not provided)
            
        Returns:
            str: Path to the generated QIF file
            
        Raises:
            CSVToQIFServiceError: If the conversion fails
        """
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_content = file.read()
            
            qif_content = self.convert_csv_to_qif(csv_content, template, account_name)
            
            if not qif_file_path:
                base_path, _ = os.path.splitext(csv_file_path)
                qif_file_path = f"{base_path}.qif"
            
            with open(qif_file_path, 'w', encoding='utf-8') as file:
                file.write(qif_content)
            
            return qif_file_path
            
        except Exception as e:
            if isinstance(e, CSVToQIFServiceError):
                raise
            raise CSVToQIFServiceError(f"Failed to convert CSV file to QIF file: {str(e)}")
