import pytest
import os
import tempfile
import json
from unittest.mock import patch, mock_open

from quickenqifimport.utils.template_utils import (
    load_template, save_template, list_templates,
    get_default_templates, create_template, delete_template,
    validate_template
)
from quickenqifimport.models.models import CSVTemplate, AccountType

class TestTemplateUtils:
    """Unit tests for template utility functions."""
    
    def test_load_template(self):
        """Test loading template from file."""
        template_data = {
            "name": "test_template",
            "account_type": "BANK",
            "field_mapping": {
                "date": "Date",
                "amount": "Amount",
                "payee": "Description"
            },
            "date_format": "%Y-%m-%d"
        }
        
        with patch("builtins.open", mock_open(read_data=json.dumps(template_data))):
            with patch("os.path.exists", return_value=True):
                template = load_template("test_template")
                
                assert isinstance(template, CSVTemplate)
                assert template.name == "test_template"
                assert template.account_type == AccountType.BANK
                assert template.field_mapping["date"] == "Date"
                assert template.field_mapping["amount"] == "Amount"
                assert template.field_mapping["payee"] == "Description"
                assert template.date_format == "%Y-%m-%d"
        
        with patch("os.path.exists", return_value=False):
            with pytest.raises(FileNotFoundError):
                load_template("non_existent_template")
    
    def test_save_template(self):
        """Test saving template to file."""
        template = CSVTemplate(
            name="test_template",
            account_type=AccountType.BANK,
            field_mapping={
                "date": "Date",
                "amount": "Amount",
                "payee": "Description"
            },
            date_format="%Y-%m-%d"
        )
        
        mock = mock_open()
        with patch("builtins.open", mock):
            with patch("quickenqifimport.utils.template_utils.ensure_directory_exists"):
                save_template(template)
        
        mock.assert_called_once()
        written_data = mock().write.call_args[0][0]
        loaded_data = json.loads(written_data)
        
        assert loaded_data["name"] == "test_template"
        assert loaded_data["account_type"] == "BANK"
        assert loaded_data["field_mapping"]["date"] == "Date"
        assert loaded_data["field_mapping"]["amount"] == "Amount"
        assert loaded_data["field_mapping"]["payee"] == "Description"
        assert loaded_data["date_format"] == "%Y-%m-%d"
    
    def test_list_templates(self):
        """Test listing available templates."""
        with tempfile.TemporaryDirectory() as temp_dir:
            template1 = os.path.join(temp_dir, "template1.json")
            template2 = os.path.join(temp_dir, "template2.json")
            non_template = os.path.join(temp_dir, "file.txt")
            
            with open(template1, "w") as f:
                f.write(json.dumps({"name": "template1"}))
            with open(template2, "w") as f:
                f.write(json.dumps({"name": "template2"}))
            with open(non_template, "w") as f:
                f.write("test")
            
            with patch("quickenqifimport.utils.template_utils.get_template_directory") as mock_get_dir:
                mock_get_dir.return_value = temp_dir
                
                templates = list_templates()
                
                assert len(templates) == 2
                assert "template1" in templates
                assert "template2" in templates
    
    def test_get_default_templates(self):
        """Test getting default templates."""
        with patch("quickenqifimport.utils.template_utils.list_templates") as mock_list:
            mock_list.return_value = []
            
            templates = get_default_templates()
            
            assert len(templates) >= 2
            
            template_names = [t.name for t in templates]
            assert "bank_default" in template_names
            assert "investment_default" in template_names
            
            bank_template = next(t for t in templates if t.name == "bank_default")
            assert bank_template.account_type == AccountType.BANK
            assert "date" in bank_template.field_mapping
            assert "amount" in bank_template.field_mapping
            
            investment_template = next(t for t in templates if t.name == "investment_default")
            assert investment_template.account_type == AccountType.INVESTMENT
            assert "date" in investment_template.field_mapping
            assert "security" in investment_template.field_mapping
    
    def test_create_template(self):
        """Test creating a new template."""
        template_data = {
            "name": "new_template",
            "account_type": "BANK",
            "field_mapping": {
                "date": "Date",
                "amount": "Amount"
            },
            "date_format": "%Y-%m-%d"
        }
        
        with patch("quickenqifimport.utils.template_utils.save_template") as mock_save:
            template = create_template(template_data)
            
            assert isinstance(template, CSVTemplate)
            assert template.name == "new_template"
            assert template.account_type == AccountType.BANK
            
            mock_save.assert_called_once_with(template)
    
    def test_delete_template(self):
        """Test deleting a template."""
        with patch("os.path.exists", return_value=True):
            with patch("os.remove") as mock_remove:
                with patch("quickenqifimport.utils.template_utils.get_template_path") as mock_path:
                    mock_path.return_value = "/path/to/template.json"
                    
                    delete_template("test_template")
                    
                    mock_remove.assert_called_once_with("/path/to/template.json")
        
        with patch("os.path.exists", return_value=False):
            with pytest.raises(FileNotFoundError):
                delete_template("non_existent_template")
    
    def test_validate_template(self):
        """Test template validation."""
        valid_template = {
            "name": "valid_template",
            "account_type": "BANK",
            "field_mapping": {
                "date": "Date",
                "amount": "Amount",
                "payee": "Description"
            },
            "date_format": "%Y-%m-%d"
        }
        assert validate_template(valid_template) is True
        
        invalid_template = {
            "name": "invalid_template",
            "account_type": "BANK"
        }
        assert validate_template(invalid_template) is False
        
        invalid_template = {
            "name": "invalid_template",
            "account_type": "INVALID_TYPE",
            "field_mapping": {
                "date": "Date",
                "amount": "Amount"
            }
        }
        assert validate_template(invalid_template) is False
