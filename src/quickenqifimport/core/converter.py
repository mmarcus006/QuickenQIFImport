from typing import Optional, Dict, Any, List, Union
import os

from ..models.qif_models import QIFAccountType, QIFFile
from ..models.csv_models import CSVTemplate
from ..parsers.qif_parser import QIFParser
from ..parsers.csv_parser import CSVParser
from ..converters.qif_to_csv_converter import QIFToCSVConverter
from ..converters.csv_to_qif_converter import CSVToQIFConverter
from ..utils.file_utils import FileUtils


class Converter:
    """Core converter class that orchestrates the conversion process."""
    
    def __init__(self):
        self.qif_parser = QIFParser()
        self.csv_parser = CSVParser()
        self.qif_to_csv_converter = QIFToCSVConverter()
        self.csv_to_qif_converter = CSVToQIFConverter()
    
    def convert_qif_to_csv(self, qif_file_path: str, csv_file_path: str, 
                          template: Optional[CSVTemplate] = None,
                          date_format: str = "%Y-%m-%d",
                          delimiter: str = ",") -> None:
        """
        Convert a QIF file to a CSV file.
        
        Args:
            qif_file_path: Path to the QIF file
            csv_file_path: Path to save the CSV file
            template: Optional template for field mapping
            date_format: Date format for the CSV file
            delimiter: Delimiter for the CSV file
            
        Raises:
            FileNotFoundError: If the QIF file does not exist
            ValueError: If the QIF file is invalid
            OSError: If the CSV file cannot be written
        """
        if not os.path.isfile(qif_file_path):
            raise FileNotFoundError(f"QIF file not found: {qif_file_path}")
            
        if not FileUtils.is_qif_file(qif_file_path):
            raise ValueError(f"Not a QIF file: {qif_file_path}")
            
        self.qif_to_csv_converter.date_format = date_format
        self.qif_to_csv_converter.delimiter = delimiter
        
        self.qif_to_csv_converter.convert_file(qif_file_path, csv_file_path, template)
    
    def convert_csv_to_qif(self, csv_file_path: str, qif_file_path: str, 
                          account_type: Union[QIFAccountType, str],
                          template: Optional[CSVTemplate] = None,
                          date_format: str = "%Y-%m-%d") -> None:
        """
        Convert a CSV file to a QIF file.
        
        Args:
            csv_file_path: Path to the CSV file
            qif_file_path: Path to save the QIF file
            account_type: QIF account type
            template: Optional template for field mapping
            date_format: Date format for the CSV file
            
        Raises:
            FileNotFoundError: If the CSV file does not exist
            ValueError: If the CSV file is invalid or the account type is invalid
            OSError: If the QIF file cannot be written
        """
        if not os.path.isfile(csv_file_path):
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
            
        if not FileUtils.is_csv_file(csv_file_path):
            raise ValueError(f"Not a CSV file: {csv_file_path}")
            
        if isinstance(account_type, str):
            try:
                account_type = QIFAccountType(account_type)
            except ValueError:
                raise ValueError(f"Invalid account type: {account_type}")
                
        self.csv_to_qif_converter.date_format = date_format
        
        self.csv_to_qif_converter.convert_file(csv_file_path, qif_file_path, account_type, template)
    
    def detect_file_type(self, file_path: str) -> str:
        """
        Detect the type of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            str: 'qif', 'csv', or 'unknown'
            
        Raises:
            FileNotFoundError: If the file does not exist
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        extension = FileUtils.get_file_extension(file_path)
        
        if extension == 'qif':
            return 'qif'
        elif extension == 'csv':
            return 'csv'
        else:
            return 'unknown'
    
    def detect_qif_account_type(self, qif_file_path: str) -> QIFAccountType:
        """
        Detect the account type of a QIF file.
        
        Args:
            qif_file_path: Path to the QIF file
            
        Returns:
            QIFAccountType: The detected account type
            
        Raises:
            FileNotFoundError: If the QIF file does not exist
            ValueError: If the QIF file is invalid
        """
        qif_file = self.qif_parser.parse_file(qif_file_path)
        
        return qif_file.type
    
    def detect_csv_template_type(self, csv_file_path: str) -> Optional[str]:
        """
        Detect the template type for a CSV file.
        
        Args:
            csv_file_path: Path to the CSV file
            
        Returns:
            Optional[str]: The detected template type or None
            
        Raises:
            FileNotFoundError: If the CSV file does not exist
        """
        return self.csv_parser.detect_template(csv_file_path)
    
    def preview_qif_file(self, qif_file_path: str, max_transactions: int = 5) -> Dict[str, Any]:
        """
        Preview the contents of a QIF file.
        
        Args:
            qif_file_path: Path to the QIF file
            max_transactions: Maximum number of transactions to include in the preview
            
        Returns:
            Dict[str, Any]: Preview information
            
        Raises:
            FileNotFoundError: If the QIF file does not exist
            ValueError: If the QIF file is invalid
        """
        qif_file = self.qif_parser.parse_file(qif_file_path)
        
        preview = {
            'account_type': qif_file.type.value,
            'transactions': []
        }
        
        if qif_file.type == QIFAccountType.BANK and qif_file.bank_transactions:
            preview['transactions'] = [t.model_dump() for t in qif_file.bank_transactions[:max_transactions]]
        elif qif_file.type == QIFAccountType.CASH and qif_file.cash_transactions:
            preview['transactions'] = [t.model_dump() for t in qif_file.cash_transactions[:max_transactions]]
        elif qif_file.type == QIFAccountType.CCARD and qif_file.credit_card_transactions:
            preview['transactions'] = [t.model_dump() for t in qif_file.credit_card_transactions[:max_transactions]]
        elif qif_file.type == QIFAccountType.INVESTMENT and qif_file.investment_transactions:
            preview['transactions'] = [t.model_dump() for t in qif_file.investment_transactions[:max_transactions]]
        elif qif_file.type == QIFAccountType.ASSET and qif_file.asset_transactions:
            preview['transactions'] = [t.model_dump() for t in qif_file.asset_transactions[:max_transactions]]
        elif qif_file.type == QIFAccountType.LIABILITY and qif_file.liability_transactions:
            preview['transactions'] = [t.model_dump() for t in qif_file.liability_transactions[:max_transactions]]
        elif qif_file.type == QIFAccountType.ACCOUNT and qif_file.accounts:
            preview['accounts'] = [a.model_dump() for a in qif_file.accounts[:max_transactions]]
        elif qif_file.type == QIFAccountType.CATEGORY and qif_file.categories:
            preview['categories'] = [c.model_dump() for c in qif_file.categories[:max_transactions]]
        elif qif_file.type == QIFAccountType.CLASS and qif_file.classes:
            preview['classes'] = [c.model_dump() for c in qif_file.classes[:max_transactions]]
        elif qif_file.type == QIFAccountType.MEMORIZED and qif_file.memorized_transactions:
            preview['memorized_transactions'] = [t.model_dump() for t in qif_file.memorized_transactions[:max_transactions]]
            
        return preview
    
    def preview_csv_file(self, csv_file_path: str, max_rows: int = 5) -> Dict[str, Any]:
        """
        Preview the contents of a CSV file.
        
        Args:
            csv_file_path: Path to the CSV file
            max_rows: Maximum number of rows to include in the preview
            
        Returns:
            Dict[str, Any]: Preview information
            
        Raises:
            FileNotFoundError: If the CSV file does not exist
            ValueError: If the CSV file is invalid
        """
        delimiter = FileUtils.detect_csv_delimiter(csv_file_path)
        
        rows = self.csv_parser.parse_file(csv_file_path)
        
        preview = {
            'delimiter': delimiter,
            'headers': list(rows[0].keys()) if rows else [],
            'rows': rows[:max_rows]
        }
        
        template_type = self.detect_csv_template_type(csv_file_path)
        if template_type:
            preview['template_type'] = template_type
            
        return preview
