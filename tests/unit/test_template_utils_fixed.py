import pytest
import os
import tempfile
from unittest.mock import patch, mock_open, MagicMock

from quickenqifimport.utils.template_utils import (
    get_templates_directory, list_templates, load_template,
    save_template, delete_template, create_default_templates,
    TemplateError
)
from quickenqifimport.models.models import CSVTemplate, AccountType

class TestTemplateUtils:
    """Unit tests for template utility functions."""
    
    @pytest.fixture
    def temp_templates_dir(self):
        """Fixture for temporary templates directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_env = os.environ.get('QIF_TEMPLATES_DIR')
            
            os.environ['QIF_TEMPLATES_DIR'] = temp_dir
            
            yield temp_dir
            
            if original_env:
                os.environ['QIF_TEMPLATES_DIR'] = original_env
            else:
                os.environ.pop('QIF_TEMPLATES_DIR', None)
    
    def test_get_templates_directory(self, temp_templates_dir):
        """Test getting templates directory."""
        templates_dir = get_templates_directory()
        assert templates_dir == temp_templates_dir
        
        with patch.dict(os.environ, {}, clear=True):
            templates_dir = get_templates_directory()
            assert templates_dir.endswith('.qif_converter/templates')
            assert os.path.isdir(templates_dir)
    
    def test_list_templates(self, temp_templates_dir):
        """Test listing templates."""
        template1_path = os.path.join(temp_templates_dir, "template1.yaml")
        template2_path = os.path.join(temp_templates_dir, "template2.yaml")
        non_template_path = os.path.join(temp_templates_dir, "file.txt")
        
        with open(template1_path, "w") as f:
            f.write("name: template1")
        with open(template2_path, "w") as f:
            f.write("name: template2")
        with open(non_template_path, "w") as f:
            f.write("test")
        
        templates = list_templates()
        
        assert len(templates) == 2
        assert "template1" in templates
        assert "template2" in templates
    
    def test_load_template(self, temp_templates_dir):
        """Test loading template."""
        template_data = {
            "name": "test_template",
            "account_type": "Bank",  # Use the actual enum value string
            "field_mapping": {
                "date": "Date",
                "amount": "Amount"
            }
        }
        
        template_path = os.path.join(temp_templates_dir, "test_template.yaml")
        
        with patch("quickenqifimport.utils.template_utils.load_yaml") as mock_load:
            mock_load.return_value = template_data
            
            with patch("os.path.exists", return_value=True):
                with patch("quickenqifimport.utils.template_utils.CSVTemplate") as mock_template_class:
                    mock_template = MagicMock()
                    mock_template.name = "test_template"
                    mock_template.account_type = AccountType.BANK
                    mock_template.field_mapping = {"date": "Date", "amount": "Amount"}
                    mock_template_class.return_value = mock_template
                    
                    template = load_template("test_template")
                    
                    assert template.name == "test_template"
                    assert template.account_type == AccountType.BANK
                    assert "date" in template.field_mapping
                    assert "amount" in template.field_mapping
        
        with patch("os.path.exists", return_value=False):
            with pytest.raises(TemplateError):
                load_template("non_existent_template")
    
    def test_save_template(self, temp_templates_dir):
        """Test saving template."""
        mock_template = MagicMock()
        mock_template.name = "test_template"
        mock_template.account_type = AccountType.BANK
        mock_template.field_mapping = {"date": "Date", "amount": "Amount"}
        mock_template.model_dump.return_value = {
            "name": "test_template",
            "account_type": "Bank",
            "field_mapping": {"date": "Date", "amount": "Amount"}
        }
        
        with patch("quickenqifimport.utils.template_utils.save_yaml") as mock_save:
            save_template(mock_template)
            
            mock_save.assert_called_once()
            args, kwargs = mock_save.call_args
            
            assert args[0].endswith("test_template.yaml")
            assert args[1]["name"] == "test_template"
            assert args[1]["account_type"] == "Bank"
            assert "date" in args[1]["field_mapping"]
            assert "amount" in args[1]["field_mapping"]
        
        mock_unnamed = MagicMock()
        mock_unnamed.name = ""  # Empty name
        
        with pytest.raises(TemplateError):
            save_template(mock_unnamed)
    
    def test_delete_template(self, temp_templates_dir):
        """Test deleting template."""
        template_path = os.path.join(temp_templates_dir, "template_to_delete.yaml")
        with open(template_path, "w") as f:
            f.write("name: template_to_delete")
        
        delete_template("template_to_delete")
        
        assert not os.path.exists(template_path)
        
        with pytest.raises(TemplateError):
            delete_template("non_existent_template")
    
    def test_create_default_templates(self, temp_templates_dir):
        """Test creating default templates."""
        with patch("quickenqifimport.utils.template_utils.save_template") as mock_save:
            create_default_templates()
            
            assert mock_save.call_count == 3
