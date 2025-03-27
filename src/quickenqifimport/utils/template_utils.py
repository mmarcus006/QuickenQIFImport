import os
from typing import Dict, List, Optional, Any
import yaml
from ..models.models import CSVTemplate, AccountType
from .file_utils import load_yaml, save_yaml

class TemplateError(Exception):
    """Exception raised for errors related to CSV templates."""
    pass

def get_templates_directory() -> str:
    """Get the directory where templates are stored.
    
    Returns:
        str: Path to the templates directory
    """
    templates_dir = os.environ.get('QIF_TEMPLATES_DIR')
    
    if templates_dir:
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir, exist_ok=True)
        return templates_dir
    
    home_dir = os.path.expanduser('~')
    templates_dir = os.path.join(home_dir, '.qif_converter', 'templates')
    
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir, exist_ok=True)
        
    return templates_dir

get_templates_dir = get_templates_directory

def list_templates() -> List[str]:
    """List all available template names.
    
    Returns:
        List[str]: List of template names
    """
    templates_dir = get_templates_directory()
    template_files = [f for f in os.listdir(templates_dir) 
                     if f.endswith('.yaml') and os.path.isfile(os.path.join(templates_dir, f))]
    
    return [os.path.splitext(f)[0] for f in template_files]

def load_template(name: str) -> CSVTemplate:
    """Load a template by name.
    
    Args:
        name: Name of the template to load
        
    Returns:
        CSVTemplate: The loaded template
        
    Raises:
        TemplateError: If the template cannot be found or loaded
    """
    templates_dir = get_templates_directory()
    template_path = os.path.join(templates_dir, f"{name}.yaml")
    
    if not os.path.exists(template_path):
        raise TemplateError(f"Template '{name}' not found")
    
    try:
        template_data = load_yaml(template_path)
        return CSVTemplate(**template_data)
    except Exception as e:
        raise TemplateError(f"Failed to load template '{name}': {str(e)}")

def save_template(template: CSVTemplate) -> None:
    """Save a template.
    
    Args:
        template: Template to save
        
    Raises:
        TemplateError: If the template cannot be saved
    """
    if not template.name:
        raise TemplateError("Template must have a name")
    
    templates_dir = get_templates_directory()
    template_path = os.path.join(templates_dir, f"{template.name}.yaml")
    
    try:
        template_dict = template.model_dump()
        save_yaml(template_path, template_dict)
    except Exception as e:
        raise TemplateError(f"Failed to save template '{template.name}': {str(e)}")

def delete_template(name: str) -> None:
    """Delete a template by name.
    
    Args:
        name: Name of the template to delete
        
    Raises:
        TemplateError: If the template cannot be found or deleted
    """
    templates_dir = get_templates_directory()
    template_path = os.path.join(templates_dir, f"{name}.yaml")
    
    if not os.path.exists(template_path):
        raise TemplateError(f"Template '{name}' not found")
    
    try:
        os.remove(template_path)
    except Exception as e:
        raise TemplateError(f"Failed to delete template '{name}': {str(e)}")

def create_default_templates() -> None:
    """Create default templates for common financial institutions.
    
    This function creates a set of predefined templates for common banks,
    credit cards, and investment accounts.
    """
    bank_template = CSVTemplate(
        name="generic_bank",
        description="Generic bank transaction template",
        account_type=AccountType.BANK,
        delimiter=",",
        has_header=True,
        date_format="%Y-%m-%d",
        field_mapping={
            "date": "Date",
            "amount": "Amount",
            "payee": "Description",
            "number": "Reference",
            "memo": "Memo",
            "category": "Category",
            "account": "Account Name",
            "cleared_status": "Status"
        },
        skip_rows=0,
        amount_columns=["Amount"],
        amount_multiplier={},
        category_format="Category:Subcategory",
        detect_transfers=True,
        transfer_pattern=r"\[(.*?)\]"
    )
    
    credit_card_template = CSVTemplate(
        name="generic_credit_card",
        description="Generic credit card transaction template",
        account_type=AccountType.CREDIT_CARD,
        delimiter=",",
        has_header=True,
        date_format="%Y-%m-%d",
        field_mapping={
            "date": "Date",
            "amount": "Amount",
            "payee": "Description",
            "memo": "Memo",
            "category": "Category",
            "cleared_status": "Status"
        },
        skip_rows=0,
        amount_columns=["Amount"],
        amount_multiplier={},
        category_format="Category:Subcategory",
        detect_transfers=True,
        transfer_pattern=r"\[(.*?)\]"
    )
    
    investment_template = CSVTemplate(
        name="generic_investment",
        description="Generic investment transaction template",
        account_type=AccountType.INVESTMENT,
        delimiter=",",
        has_header=True,
        date_format="%Y-%m-%d",
        field_mapping={
            "date": "Date",
            "action": "Action",
            "security": "Security",
            "quantity": "Quantity",
            "price": "Price",
            "amount": "Amount",
            "commission": "Commission",
            "payee": "Description",
            "category": "Category",
            "account": "Account",
            "memo": "Memo",
            "cleared_status": "Status"
        },
        skip_rows=0,
        amount_columns=["Amount", "Price", "Commission"],
        amount_multiplier={},
        category_format="Category:Subcategory",
        detect_transfers=True,
        transfer_pattern=r"\[(.*?)\]"
    )
    
    try:
        save_template(bank_template)
        save_template(credit_card_template)
        save_template(investment_template)
    except TemplateError as e:
        print(f"Warning: Failed to create default templates: {str(e)}")
