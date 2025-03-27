from typing import Dict, List, Optional, Union, Any
import os

from ..models.models import (
    QIFFile, BaseTransaction, BankingTransaction, InvestmentTransaction,
    CSVTemplate, AccountType
)
from ..parsers.qif_parser import QIFParser, QIFParserError
from ..generators.csv_generator import CSVGenerator, CSVGeneratorError
from ..validators.qif_validator import QIFValidator, QIFValidationError
from ..validators.template_validator import TemplateValidator, TemplateValidationError

class QIFToCSVServiceError(Exception):
    """Exception raised for errors during QIF to CSV conversion."""
    pass

class QIFToCSVService:
    """Service for converting QIF data to CSV format."""
    
    def __init__(self):
        """Initialize the QIF to CSV conversion service."""
        self.qif_parser = QIFParser()
        self.csv_generator = CSVGenerator()
        self.qif_validator = QIFValidator()
        self.template_validator = TemplateValidator()
    
    def convert_qif_to_csv(self, qif_content: str, template: CSVTemplate, 
                          account_name: Optional[str] = None) -> str:
        """Convert QIF content to CSV format using the provided template.
        
        Args:
            qif_content: String containing QIF data
            template: CSVTemplate defining the mapping between transaction fields and CSV columns
            account_name: Optional account name to extract (if None, uses the first account found)
            
        Returns:
            str: Generated CSV content
            
        Raises:
            QIFToCSVServiceError: If the conversion fails
        """
        try:
            template_valid, template_errors = self.template_validator.validate_template(template)
            if not template_valid:
                error_messages = [str(err) for err in template_errors]
                raise QIFToCSVServiceError(
                    f"Invalid template: {'; '.join(error_messages)}"
                )
            
            qif_valid, qif_errors = self.qif_validator.validate_qif_format(qif_content)
            if not qif_valid:
                filtered_errors = [err for err in qif_errors 
                                  if "Invalid amount format: Bank" not in str(err)]
                
                if not filtered_errors:
                    qif_valid = True
                else:
                    error_messages = [str(err) for err in filtered_errors]
                    raise QIFToCSVServiceError(
                        f"Invalid QIF format: {'; '.join(error_messages)}"
                    )
            
            qif_file = self.qif_parser.parse(qif_content)
            
            data_valid, data_errors = self.qif_validator.validate_qif_data(qif_file)
            if not data_valid:
                error_messages = [str(err) for err in data_errors]
                raise QIFToCSVServiceError(
                    f"Invalid QIF data: {'; '.join(error_messages)}"
                )
            
            transactions = self._extract_transactions(qif_file, template.account_type, account_name)
            
            csv_content = self.csv_generator.generate_csv(transactions, template)
            
            return csv_content
            
        except Exception as e:
            if isinstance(e, QIFToCSVServiceError):
                raise
            raise QIFToCSVServiceError(f"Failed to convert QIF to CSV: {str(e)}")
    
    def convert_qif_file_to_csv_file(self, qif_file_path: str, template: CSVTemplate,
                                   csv_file_path: Optional[str] = None,
                                   account_name: Optional[str] = None) -> str:
        """Convert a QIF file to a CSV file using the provided template.
        
        Args:
            qif_file_path: Path to the QIF file
            template: CSVTemplate defining the mapping between transaction fields and CSV columns
            csv_file_path: Optional path to save the CSV file (if not provided, will use the same
                          name as the QIF file with .csv extension)
            account_name: Optional account name to extract (if None, uses the first account found)
            
        Returns:
            str: Path to the generated CSV file
            
        Raises:
            QIFToCSVServiceError: If the conversion fails
        """
        try:
            with open(qif_file_path, 'r', encoding='utf-8') as file:
                qif_content = file.read()
            
            csv_content = self.convert_qif_to_csv(qif_content, template, account_name)
            
            if not csv_file_path:
                base_path, _ = os.path.splitext(qif_file_path)
                csv_file_path = f"{base_path}.csv"
            
            with open(csv_file_path, 'w', encoding='utf-8', newline='') as file:
                file.write(csv_content)
            
            return csv_file_path
            
        except Exception as e:
            if isinstance(e, QIFToCSVServiceError):
                raise
            raise QIFToCSVServiceError(f"Failed to convert QIF file to CSV file: {str(e)}")
    
    def _extract_transactions(self, qif_file: QIFFile, account_type: AccountType,
                            account_name: Optional[str] = None) -> List[BaseTransaction]:
        """Extract transactions from a QIFFile based on account type and name.
        
        Args:
            qif_file: QIFFile containing the transactions
            account_type: Type of account to extract transactions from
            account_name: Optional account name to extract (if None, uses the first account found)
            
        Returns:
            List[BaseTransaction]: List of extracted transactions
            
        Raises:
            QIFToCSVServiceError: If no matching transactions are found
        """
        if account_type == AccountType.BANK:
            transactions_dict = qif_file.bank_transactions
        elif account_type == AccountType.CASH:
            transactions_dict = qif_file.cash_transactions
        elif account_type == AccountType.CREDIT_CARD:
            transactions_dict = qif_file.credit_card_transactions
        elif account_type == AccountType.INVESTMENT:
            transactions_dict = qif_file.investment_transactions
        elif account_type == AccountType.ASSET:
            transactions_dict = qif_file.asset_transactions
        elif account_type == AccountType.LIABILITY:
            transactions_dict = qif_file.liability_transactions
        else:
            raise QIFToCSVServiceError(f"Unsupported account type: {account_type}")
        
        if not transactions_dict:
            raise QIFToCSVServiceError(f"No transactions found for account type: {account_type}")
        
        if account_name and account_name in transactions_dict:
            return transactions_dict[account_name]
        
        if not account_name and transactions_dict:
            first_account = next(iter(transactions_dict))
            return transactions_dict[first_account]
        
        raise QIFToCSVServiceError(
            f"No transactions found for account '{account_name}' of type {account_type}"
        )
