from typing import Union, Optional
import re


class AmountUtils:
    """Utility class for amount operations."""
    
    @staticmethod
    def parse_amount(amount_str: str, decimal_separator: str = '.', thousand_separator: str = ',') -> float:
        """
        Parse an amount string to a float.
        
        Args:
            amount_str: The amount string to parse
            decimal_separator: The decimal separator character
            thousand_separator: The thousand separator character
            
        Returns:
            float: The parsed amount
            
        Raises:
            ValueError: If the amount string cannot be parsed
        """
        if not amount_str:
            return 0.0
        
        is_negative = False
        if amount_str.startswith('(') and amount_str.endswith(')'):
            amount_str = amount_str[1:-1]
            is_negative = True
        
        amount_str = amount_str.replace('$', '')
        
        if amount_str.startswith('-$'):
            amount_str = '-' + amount_str[2:]
        elif amount_str.startswith('-'):
            is_negative = True
            amount_str = amount_str[1:]
            
        amount_str = re.sub(r'[^\d' + re.escape(decimal_separator) + re.escape(thousand_separator) + r'\-+]', '', amount_str)
        
        amount_str = amount_str.replace(thousand_separator, '')
        
        if decimal_separator != '.':
            amount_str = amount_str.replace(decimal_separator, '.')
            
        try:
            result = float(amount_str)
            return -result if is_negative else result
        except ValueError:
            raise ValueError(f"Could not parse amount: {amount_str}")
    
    @staticmethod
    def format_amount(amount: Union[float, int], decimal_places: int = 2, decimal_separator: str = '.', 
                     thousand_separator: str = ',', include_sign: bool = False, include_currency: bool = False) -> str:
        """
        Format an amount as a string.
        
        Args:
            amount: The amount to format
            decimal_places: The number of decimal places
            decimal_separator: The decimal separator character
            thousand_separator: The thousand separator character
            include_sign: Whether to include a + sign for positive amounts
            include_currency: Whether to include the currency symbol ($)
            
        Returns:
            str: The formatted amount string
        """
        abs_amount = abs(amount)
        if decimal_places == 0:
            rounded = round(abs_amount)
            amount_str = f"{rounded}"
        else:
            amount_str = f"{abs_amount:.{decimal_places}f}"
        
        if '.' in amount_str:
            int_part, dec_part = amount_str.split('.')
        else:
            int_part, dec_part = amount_str, ''
            
        int_part = AmountUtils._add_thousand_separators(int_part, thousand_separator)
        
        if decimal_places > 0:
            amount_str = f"{int_part}{decimal_separator}{dec_part}"
        else:
            amount_str = int_part
            
        if amount < 0:
            amount_str = f"-{amount_str}"
        elif include_sign and amount > 0:
            amount_str = f"+{amount_str}"
        
        if include_currency and amount >= 0:
            amount_str = f"${amount_str}"
        elif include_currency and amount < 0:
            amount_str = f"-${amount_str.lstrip('-')}"
            
        return amount_str
    
    @staticmethod
    def _add_thousand_separators(int_part: str, thousand_separator: str) -> str:
        """
        Add thousand separators to the integer part of an amount.
        
        Args:
            int_part: The integer part of the amount
            thousand_separator: The thousand separator character
            
        Returns:
            str: The integer part with thousand separators
        """
        result = ''
        for i, char in enumerate(reversed(int_part)):
            if i > 0 and i % 3 == 0:
                result = thousand_separator + result
            result = char + result
        return result
    
    @staticmethod
    def is_negative(amount_str: str, decimal_separator: str = '.', thousand_separator: str = ',') -> bool:
        """
        Check if an amount string represents a negative amount.
        
        Args:
            amount_str: The amount string to check
            decimal_separator: The decimal separator character
            thousand_separator: The thousand separator character
            
        Returns:
            bool: True if the amount is negative, False otherwise
        """
        amount_str = amount_str.strip()
        
        return amount_str.startswith('-') or (amount_str.startswith('(') and amount_str.endswith(')'))
    
    @staticmethod
    def convert_to_qif_format(amount: Union[float, int, str], decimal_separator: str = '.', 
                             thousand_separator: str = ',') -> str:
        """
        Convert an amount to QIF format (no thousand separators, dot as decimal separator).
        
        Args:
            amount: The amount to convert
            decimal_separator: The decimal separator character in the input if it's a string
            thousand_separator: The thousand separator character in the input if it's a string
            
        Returns:
            str: The amount in QIF format
        """
        if isinstance(amount, str):
            if amount.startswith('(') and amount.endswith(')'):
                amount = '-' + amount[1:-1]
            
            amount = amount.replace('$', '')
            
            if amount.startswith('-$'):
                amount = '-' + amount[2:]
                
            amount = AmountUtils.parse_amount(amount, decimal_separator, thousand_separator)
            
        return f"{amount:.2f}"
