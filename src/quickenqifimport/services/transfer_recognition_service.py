from typing import Dict, List, Tuple, Optional, Union, Any
import re
from datetime import datetime, timedelta

from ..models.models import BaseTransaction, BankingTransaction, InvestmentTransaction

class TransferRecognitionServiceError(Exception):
    """Exception raised for errors during transfer recognition."""
    pass

class TransferRecognitionService:
    """Service for identifying and managing transfer transactions."""
    
    def __init__(self, max_date_difference: int = 1, amount_tolerance: float = 0.01):
        """Initialize the transfer recognition service.
        
        Args:
            max_date_difference: Maximum number of days between matching transfers
            amount_tolerance: Maximum difference in amount for matching transfers
        """
        self.max_date_difference = max_date_difference
        self.amount_tolerance = amount_tolerance
    
    def process_transfers(self, transactions: List[BaseTransaction]) -> List[BaseTransaction]:
        """Process a list of transactions to identify and link transfers.
        
        Args:
            transactions: List of transactions to process
            
        Returns:
            List[BaseTransaction]: Processed transactions with transfer links
            
        Raises:
            TransferRecognitionServiceError: If an error occurs during processing
        """
        try:
            transfer_pairs = self.detect_transfer_pairs(transactions)
            
            for from_transaction, to_transaction in transfer_pairs:
                self.link_transfers(from_transaction, to_transaction)
            
            return transactions
            
        except Exception as e:
            raise TransferRecognitionServiceError(f"Failed to process transfers: {str(e)}")
    
    def detect_transfer_pairs(self, transactions: List[BaseTransaction]) -> List[Tuple[BaseTransaction, BaseTransaction]]:
        """Detect potential transfer pairs in a list of transactions.
        
        Args:
            transactions: List of transactions to analyze
            
        Returns:
            List[Tuple[BaseTransaction, BaseTransaction]]: List of transfer pairs
            Each pair is (from_transaction, to_transaction) where:
            - from_transaction is the source (money leaving, typically negative amount)
            - to_transaction is the destination (money arriving, typically positive amount)
        """
        transfer_pairs = []
        
        account_groups = {}
        for transaction in transactions:
            if isinstance(transaction, BankingTransaction):
                if hasattr(transaction, 'account') and transaction.account:
                    account_name = transaction.account
                    if account_name not in account_groups:
                        account_groups[account_name] = []
                    account_groups[account_name].append(transaction)
        
        for i, transaction1 in enumerate(transactions):
            if not isinstance(transaction1, BankingTransaction) or not transaction1.date or transaction1.amount is None:
                continue
            
            for j in range(i+1, len(transactions)):
                transaction2 = transactions[j]
                if not isinstance(transaction2, BankingTransaction) or not transaction2.date or transaction2.amount is None:
                    continue
                    
                if self._is_potential_transfer_match(transaction1, transaction2):
                    if transaction1.amount < 0 and transaction2.amount > 0:
                        transfer_pairs.append((transaction1, transaction2))
                    elif transaction1.amount > 0 and transaction2.amount < 0:
                        transfer_pairs.append((transaction2, transaction1))
                    elif (transaction1.payee and transaction2.payee):
                        if ("transfer to" in transaction1.payee.lower() and 
                            "transfer from" in transaction2.payee.lower()):
                            transfer_pairs.append((transaction1, transaction2))
                        elif ("transfer from" in transaction1.payee.lower() and 
                              "transfer to" in transaction2.payee.lower()):
                            transfer_pairs.append((transaction2, transaction1))
        
        return transfer_pairs
    
    def link_transfers(self, from_transaction: BaseTransaction, to_transaction: BaseTransaction) -> None:
        """Link two transactions as a transfer pair.
        
        Args:
            from_transaction: Source transaction (money leaving)
            to_transaction: Destination transaction (money arriving)
        """
        if isinstance(from_transaction, BankingTransaction) and isinstance(to_transaction, BankingTransaction):
            if hasattr(to_transaction, 'account') and to_transaction.account:
                from_transaction.category = f"[{to_transaction.account}]"
            
            if hasattr(from_transaction, 'account') and from_transaction.account:
                to_transaction.category = f"[{from_transaction.account}]"
                
            if not from_transaction.category or not to_transaction.category:
                if hasattr(from_transaction, 'payee') and from_transaction.payee:
                    match = re.search(r'to\s+(\w+)', from_transaction.payee, re.IGNORECASE)
                    if match and not from_transaction.category:
                        from_transaction.category = f"[{match.group(1)}]"
                
                if hasattr(to_transaction, 'payee') and to_transaction.payee:
                    match = re.search(r'from\s+(\w+)', to_transaction.payee, re.IGNORECASE)
                    if match and not to_transaction.category:
                        to_transaction.category = f"[{match.group(1)}]"
                        
                if not from_transaction.category and to_transaction.account:
                    from_transaction.category = f"[{to_transaction.account}]"
                if not to_transaction.category and from_transaction.account:
                    to_transaction.category = f"[{from_transaction.account}]"
        
        elif isinstance(from_transaction, InvestmentTransaction) and isinstance(to_transaction, InvestmentTransaction):
            if hasattr(to_transaction, 'account') and to_transaction.account:
                from_transaction.account = f"[{to_transaction.account}]"
            
            if hasattr(from_transaction, 'account') and from_transaction.account:
                to_transaction.account = f"[{from_transaction.account}]"
    
    def _is_potential_transfer_match(self, transaction1: BaseTransaction, 
                                   transaction2: BaseTransaction) -> bool:
        """Check if two transactions are a potential transfer match.
        
        Args:
            transaction1: First transaction
            transaction2: Second transaction
            
        Returns:
            bool: True if the transactions are a potential match, False otherwise
        """
        if transaction1.date and transaction2.date:
            date_diff = abs((transaction1.date - transaction2.date).days)
            if date_diff > self.max_date_difference:
                return False
        
        if transaction1.amount is not None and transaction2.amount is not None:
            if transaction1.amount * transaction2.amount >= 0:
                return False
            
            amount_diff = abs(abs(transaction1.amount) - abs(transaction2.amount))
            if amount_diff > self.amount_tolerance:
                return False
        
        return True
