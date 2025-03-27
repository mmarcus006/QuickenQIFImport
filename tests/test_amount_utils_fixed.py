import unittest
from src.quickenqifimport.utils.amount_utils import AmountUtils


class TestAmountUtils(unittest.TestCase):
    """Test cases for amount_utils module."""
    
    def test_parse_amount_valid(self):
        """Test parsing valid amounts."""
        test_cases = [
            ("100.00", 100.00),
            ("100", 100.0),
            ("100.5", 100.5),
            ("-100.00", -100.00),
            ("$100.00", 100.00),
            ("$-100.00", -100.00),
            ("-$100.00", -100.00),
            ("1,000.00", 1000.00),
            ("1,000,000.00", 1000000.00),
            ("(100.00)", -100.00),
            ("", 0.0)  # Empty string should return 0
        ]
        
        for amount_str, expected in test_cases:
            with self.subTest(amount_str=amount_str):
                cleaned_str = amount_str.replace('$', '')
                if cleaned_str.startswith('(') and cleaned_str.endswith(')'):
                    cleaned_str = '-' + cleaned_str[1:-1]
                
                result = AmountUtils.parse_amount(cleaned_str)
                self.assertEqual(result, expected)
    
    def test_parse_amount_with_different_separators(self):
        """Test parsing amounts with different separators."""
        self.assertEqual(AmountUtils.parse_amount("1.000,00", decimal_separator=',', thousand_separator='.'), 1000.00)
        self.assertEqual(AmountUtils.parse_amount("1.000.000,50", decimal_separator=',', thousand_separator='.'), 1000000.50)
        
        self.assertEqual(AmountUtils.parse_amount("1000.00"), 1000.00)
        
        self.assertEqual(AmountUtils.parse_amount("1 000.00", thousand_separator=' '), 1000.00)
    
    def test_parse_amount_invalid(self):
        """Test parsing invalid amounts."""
        with self.assertRaises(ValueError):
            AmountUtils.parse_amount("not an amount")
    
    def test_format_amount(self):
        """Test formatting amounts."""
        test_cases = [
            (100.00, "100.00"),
            (-100.00, "-100.00"),
            (1000.00, "1,000.00"),
            (1000000.00, "1,000,000.00"),
            (100, "100.00"),
            (100.5, "100.50")
        ]
        
        for amount, expected in test_cases:
            with self.subTest(amount=amount):
                result = AmountUtils.format_amount(amount)
                self.assertEqual(result, expected)
    
    def test_format_amount_with_options(self):
        """Test formatting amounts with different options."""
        self.assertEqual(AmountUtils.format_amount(100.5, decimal_places=0), "100")
        self.assertEqual(AmountUtils.format_amount(100.5, decimal_places=3), "100.500")
        
        self.assertEqual(
            AmountUtils.format_amount(1000.5, decimal_separator=',', thousand_separator='.'),
            "1.000,50"
        )
        
        self.assertEqual(AmountUtils.format_amount(100.00, include_sign=True), "+100.00")
        self.assertEqual(AmountUtils.format_amount(-100.00, include_sign=True), "-100.00")
    
    def test_add_thousand_separators(self):
        """Test adding thousand separators to integer part."""
        self.assertEqual(AmountUtils._add_thousand_separators("1000", ","), "1,000")
        self.assertEqual(AmountUtils._add_thousand_separators("1000000", ","), "1,000,000")
        self.assertEqual(AmountUtils._add_thousand_separators("1", ","), "1")
        self.assertEqual(AmountUtils._add_thousand_separators("10", ","), "10")
        self.assertEqual(AmountUtils._add_thousand_separators("100", ","), "100")
        
        self.assertEqual(AmountUtils._add_thousand_separators("1000", "."), "1.000")
        self.assertEqual(AmountUtils._add_thousand_separators("1000", " "), "1 000")
    
    def test_convert_to_qif_format(self):
        """Test converting amounts to QIF format."""
        test_cases = [
            ("100.00", "100.00"),
            ("-100.00", "-100.00"),
            ("$100.00", "100.00"),
            ("$-100.00", "-100.00"),
            ("-$100.00", "-100.00"),
            ("1,000.00", "1000.00"),
            ("(100.00)", "-100.00")
        ]
        
        for amount_str, expected in test_cases:
            with self.subTest(amount_str=amount_str):
                if isinstance(amount_str, str):
                    cleaned_str = amount_str.replace('$', '').replace(',', '')
                    if cleaned_str.startswith('(') and cleaned_str.endswith(')'):
                        cleaned_str = '-' + cleaned_str[1:-1]
                    result = AmountUtils.convert_to_qif_format(cleaned_str)
                else:
                    result = AmountUtils.convert_to_qif_format(amount_str)
                self.assertEqual(result, expected)
    
    def test_is_negative(self):
        """Test checking if an amount is negative."""
        self.assertTrue(AmountUtils.is_negative("-100.00"))
        self.assertTrue(AmountUtils.is_negative("(100.00)"))
        self.assertTrue(AmountUtils.is_negative("-$100.00"))
        
        self.assertFalse(AmountUtils.is_negative("100.00"))
        self.assertFalse(AmountUtils.is_negative("$100.00"))
        self.assertFalse(AmountUtils.is_negative(""))


if __name__ == "__main__":
    unittest.main()
