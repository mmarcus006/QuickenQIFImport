import os
import json
from typing import Dict, Any, List, Optional, Union
import csv
import io

from ..models.csv_models import CSVTemplate


class FileUtils:
    """Utility class for file operations."""
    
    @staticmethod
    def ensure_directory_exists(directory_path: str) -> None:
        """
        Ensure that a directory exists, creating it if necessary.
        
        Args:
            directory_path: The path to the directory
            
        Raises:
            OSError: If the directory cannot be created
        """
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
    
    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """
        Get the extension of a file.
        
        Args:
            file_path: The path to the file
            
        Returns:
            str: The file extension (lowercase, without the dot)
        """
        _, ext = os.path.splitext(file_path)
        return ext.lower()[1:] if ext else ""
    
    @staticmethod
    def is_qif_file(file_path: str) -> bool:
        """
        Check if a file is a QIF file based on its extension.
        
        Args:
            file_path: The path to the file
            
        Returns:
            bool: True if the file is a QIF file, False otherwise
        """
        return FileUtils.get_file_extension(file_path) == "qif"
    
    @staticmethod
    def is_csv_file(file_path: str) -> bool:
        """
        Check if a file is a CSV file based on its extension.
        
        Args:
            file_path: The path to the file
            
        Returns:
            bool: True if the file is a CSV file, False otherwise
        """
        return FileUtils.get_file_extension(file_path) == "csv"
    
    @staticmethod
    def save_template(template: CSVTemplate, file_path: str) -> None:
        """
        Save a template to a JSON file.
        
        Args:
            template: The template to save
            file_path: The path to the file
            
        Raises:
            OSError: If the file cannot be written
            TypeError: If the template cannot be serialized to JSON
        """
        directory = os.path.dirname(file_path)
        FileUtils.ensure_directory_exists(directory)
        
        template_dict = template.model_dump()
        
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(template_dict, file, indent=4)
    
    @staticmethod
    def load_template(file_path: str) -> CSVTemplate:
        """
        Load a template from a JSON file.
        
        Args:
            file_path: The path to the file
            
        Returns:
            CSVTemplate: The loaded template
            
        Raises:
            FileNotFoundError: If the file does not exist
            json.JSONDecodeError: If the file is not valid JSON
            ValueError: If the JSON does not represent a valid template
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            template_dict = json.load(file)
            
        return CSVTemplate(**template_dict)
    
    @staticmethod
    def list_templates(directory_path: str) -> List[str]:
        """
        List all template files in a directory.
        
        Args:
            directory_path: The path to the directory
            
        Returns:
            List[str]: List of template file names
            
        Raises:
            FileNotFoundError: If the directory does not exist
        """
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")
            
        return [f for f in os.listdir(directory_path) if f.endswith('.json')]
    
    @staticmethod
    def detect_csv_delimiter(file_path: str, sample_size: int = 5) -> str:
        """
        Detect the delimiter used in a CSV file.
        
        Args:
            file_path: The path to the file
            sample_size: The number of lines to sample
            
        Returns:
            str: The detected delimiter
            
        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the delimiter cannot be detected
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            sample_lines = [file.readline() for _ in range(sample_size)]
            
        delimiters = [',', ';', '\t', '|']
        counts = {delimiter: sum(line.count(delimiter) for line in sample_lines) for delimiter in delimiters}
        
        consistent_counts = {}
        for delimiter, total_count in counts.items():
            if total_count == 0:
                continue
                
            avg_count = total_count / len(sample_lines)
            
            consistency = sum(1 for line in sample_lines if line.count(delimiter) > 0) / len(sample_lines)
            
            consistent_counts[delimiter] = consistency * avg_count
            
        if not consistent_counts:
            return ','
            
        return max(consistent_counts.items(), key=lambda x: x[1])[0]
    
    @staticmethod
    def get_csv_headers(file_path: str, delimiter: Optional[str] = None) -> List[str]:
        """
        Get the headers from a CSV file.
        
        Args:
            file_path: The path to the file
            delimiter: The delimiter to use, detected automatically if None
            
        Returns:
            List[str]: The CSV headers
            
        Raises:
            FileNotFoundError: If the file does not exist
            csv.Error: If the CSV file cannot be parsed
        """
        if delimiter is None:
            delimiter = FileUtils.detect_csv_delimiter(file_path)
            
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=delimiter)
            headers = next(reader)
            
        return headers
