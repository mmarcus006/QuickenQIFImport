import os
import csv
import json
import yaml
from typing import Dict, List, Any, Union, Optional, TextIO

class FileFormatError(Exception):
    """Exception raised for errors in the file format."""
    pass

def read_text_file(file_path: str) -> str:
    """Read the contents of a text file.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        str: The contents of the file
        
    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If the file cannot be read
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()
        
def write_text_file(file_path: str, content: str) -> None:
    """Write content to a text file.
    
    Args:
        file_path: Path to the file to write
        content: Content to write to the file
        
    Raises:
        PermissionError: If the file cannot be written
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
        
def read_csv_file(file_path: str, delimiter: str = ',', has_header: bool = True,
                 skip_rows: int = 0) -> Dict[str, List]:
    """Read a CSV file and return its contents.
    
    Args:
        file_path: Path to the CSV file
        delimiter: CSV delimiter character
        has_header: Whether the CSV has a header row
        skip_rows: Number of rows to skip from the beginning
        
    Returns:
        dict: A dictionary with 'headers' and 'data' keys
        
    Raises:
        FileNotFoundError: If the file does not exist
        FileFormatError: If the file format is invalid
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for _ in range(skip_rows):
                next(file, None)
                
            csv_reader = csv.reader(file, delimiter=delimiter)
            
            if has_header:
                headers = next(csv_reader, [])
                if not headers:
                    raise FileFormatError("CSV file is empty or has no headers")
            else:
                headers = [f"Column{i+1}" for i in range(len(next(csv_reader, [])))]
                file.seek(0)
                for _ in range(skip_rows):
                    next(file, None)
                csv_reader = csv.reader(file, delimiter=delimiter)
                
            data = [row for row in csv_reader]
            
            return {
                'headers': headers,
                'data': data
            }
            
    except csv.Error as e:
        raise FileFormatError(f"CSV parsing error: {str(e)}")
        
def write_csv_file(file_path: str, headers: List[str], data: List[List], 
                  delimiter: str = ',') -> None:
    """Write data to a CSV file.
    
    Args:
        file_path: Path to the CSV file
        headers: List of column headers
        data: List of rows, each row being a list of values
        delimiter: CSV delimiter character
        
    Raises:
        PermissionError: If the file cannot be written
    """
    with open(file_path, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=delimiter)
        writer.writerow(headers)
        writer.writerows(data)
        
def load_json(file_path: str) -> Any:
    """Load JSON data from a file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        The parsed JSON data
        
    Raises:
        FileNotFoundError: If the file does not exist
        json.JSONDecodeError: If the JSON cannot be parsed
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)
        
def save_json(file_path: str, data: Any, indent: int = 2) -> None:
    """Save data to a JSON file.
    
    Args:
        file_path: Path to the JSON file
        data: Data to save
        indent: Indentation level for pretty-printing
        
    Raises:
        PermissionError: If the file cannot be written
        TypeError: If the data cannot be serialized to JSON
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=indent)
        
def load_yaml(file_path: str) -> Any:
    """Load YAML data from a file.
    
    Args:
        file_path: Path to the YAML file
        
    Returns:
        The parsed YAML data
        
    Raises:
        FileNotFoundError: If the file does not exist
        yaml.YAMLError: If the YAML cannot be parsed
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)
        
def save_yaml(file_path: str, data: Any) -> None:
    """Save data to a YAML file.
    
    Args:
        file_path: Path to the YAML file
        data: Data to save
        
    Raises:
        PermissionError: If the file cannot be written
        yaml.YAMLError: If the data cannot be serialized to YAML
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, default_flow_style=False)
