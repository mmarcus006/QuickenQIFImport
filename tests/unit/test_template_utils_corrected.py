import pytest
import os
import tempfile
from unittest.mock import patch, mock_open, MagicMock

from quickenqifimport.utils.template_utils import (
    load_template, save_template, list_templates, create_default_templates,
    get_templates_dir
)
from quickenqifimport.models.models import CSVTemplate, AccountType

class TestTemplateUtils:
    """Unit tests for template utility functions."""
    
    @pytest.fixture
    def sample_template(self):
        """Sample CSV template."""
        return CSVTemplate(
            name="test_bank",
            account_type=AccountType.BANK,
            field_mapping={
                'date': 'Date',
                'amount': 'Amount',
                'payee': 'Payee',
                'category': 'Category',
                'memo': 'Memo',
                'number': 'Number'
            },
            delimiter=',',
            has_header=True,
            date_format='%Y-%m-%d'
        )
    
    def test_get_templates_dir(self):
        """Test getting templates directory."""
        templates_dir = get_templates_dir()
        assert os.path.basename(templates_dir) == "templates"
        assert os.path.isabs(templates_dir)
    
    def test_load_template(self, sample_template):
        """Test loading a template."""
        with patch('quickenqifimport.utils.template_utils.os.path.exists', return_value=True), \
             patch('quickenqifimport.utils.template_utils.load_yaml') as mock_load_yaml:
            
            mock_load_yaml.return_value = sample_template.model_dump()
            
            template = load_template("test_bank")
            
            assert template.name == "test_bank"
            assert template.account_type == AccountType.BANK
            assert template.field_mapping['date'] == 'Date'
            assert template.delimiter == ','
            assert template.has_header is True
    
    def test_load_template_not_found(self):
        """Test loading a non-existent template."""
        with patch('quickenqifimport.utils.template_utils.os.path.exists', return_value=False):
            with pytest.raises(ValueError):
                load_template("non_existent_template")
    
    def test_save_template(self, sample_template):
        """Test saving a template."""
        with patch('quickenqifimport.utils.template_utils.os.makedirs') as mock_makedirs, \
             patch('quickenqifimport.utils.template_utils.save_yaml') as mock_save_yaml:
            
            save_template(sample_template)
            
            mock_makedirs.assert_called_once()
            mock_save_yaml.assert_called_once()
    
    def test_list_templates(self):
        """Test listing templates."""
        template_files = ["template1.yaml", "template2.yaml", "not_a_template.txt"]
        
        with patch('quickenqifimport.utils.template_utils.os.path.exists', return_value=True), \
             patch('quickenqifimport.utils.template_utils.os.listdir', return_value=template_files):
            
            templates = list_templates()
            
            assert "template1" in templates
            assert "template2" in templates
            assert "not_a_template" not in templates
    
    def test_list_templates_dir_not_exists(self):
        """Test listing templates when directory doesn't exist."""
        with patch('quickenqifimport.utils.template_utils.os.path.exists', return_value=False):
            templates = list_templates()
            assert templates == []
    
    def test_create_default_templates(self):
        """Test creating default templates."""
        with patch('quickenqifimport.utils.template_utils.save_template') as mock_save_template:
            create_default_templates()
            
            assert mock_save_template.call_count >= 3
            
            templates = [call.args[0] for call in mock_save_template.call_args_list]
            template_names = [t.name for t in templates]
            
            assert "generic_bank" in template_names
            assert "generic_credit_card" in template_names
            assert "generic_investment" in template_names
            
            for template in templates:
                if template.name == "generic_bank":
                    assert template.account_type == AccountType.BANK
                elif template.name == "generic_credit_card":
                    assert template.account_type == AccountType.CREDIT_CARD
                elif template.name == "generic_investment":
                    assert template.account_type == AccountType.INVESTMENT
