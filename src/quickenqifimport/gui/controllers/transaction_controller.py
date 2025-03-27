from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject, pyqtSlot

from ..views.transaction_editor import TransactionEditor
from ...models.models import BaseTransaction, BankingTransaction, InvestmentTransaction, AccountType

class TransactionController(QObject):
    """Controller for transaction editing."""
    
    def __init__(self, parent=None):
        """Initialize the transaction controller.
        
        Args:
            parent: Parent controller or widget
        """
        super().__init__(parent)
    
    def edit_transaction(self, transaction=None, account_type=AccountType.BANK, parent=None):
        """Edit a transaction.
        
        Args:
            transaction: Transaction to edit (or None for a new transaction)
            account_type: Type of account for the transaction
            parent: Parent widget for the editor dialog
            
        Returns:
            BaseTransaction: Edited transaction, or None if canceled
        """
        editor = TransactionEditor(transaction, account_type, parent)
        
        editor.transaction_saved.connect(self._on_transaction_saved)
        
        result = editor.exec()
        
        if result == TransactionEditor.DialogCode.Accepted:
            return self.edited_transaction
        else:
            return None
    
    @pyqtSlot(BaseTransaction)
    def _on_transaction_saved(self, transaction):
        """Handle transaction saved signal.
        
        Args:
            transaction: Saved transaction
        """
        self.edited_transaction = transaction
    
    def create_transaction(self, account_type=AccountType.BANK, parent=None):
        """Create a new transaction.
        
        Args:
            account_type: Type of account for the transaction
            parent: Parent widget for the editor dialog
            
        Returns:
            BaseTransaction: Created transaction, or None if canceled
        """
        if account_type == AccountType.INVESTMENT:
            transaction = InvestmentTransaction()
        else:
            transaction = BankingTransaction()
        
        return self.edit_transaction(transaction, account_type, parent)
    
    def validate_transaction(self, transaction):
        """Validate a transaction.
        
        Args:
            transaction: Transaction to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not transaction.date:
            return False, "Date is required"
        
        if transaction.amount is None:
            return False, "Amount is required"
        
        if isinstance(transaction, InvestmentTransaction):
            if not transaction.action:
                return False, "Action is required"
            
            if not transaction.security:
                return False, "Security is required"
            
            if transaction.action in ["Buy", "Sell", "ReinvDiv", "ShrsIn", "ShrsOut", "StkSplit"]:
                if transaction.quantity is None:
                    return False, f"Quantity is required for {transaction.action} action"
            
            if transaction.action in ["Buy", "Sell", "ReinvDiv"]:
                if transaction.price is None:
                    return False, f"Price is required for {transaction.action} action"
        
        return True, ""
