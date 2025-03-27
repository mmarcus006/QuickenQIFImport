from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Union, Literal
from datetime import datetime
from enum import Enum
import re


class ClearedStatus(str, Enum):
    """Enum for transaction cleared status in QIF format."""
    UNCLEARED = ""
    CLEARED = "*"
    CLEARED_ALT = "c"
    RECONCILED = "X"
    RECONCILED_ALT = "R"


class AccountType(str, Enum):
    """Enum for QIF account types."""
    BANK = "Bank"
    CASH = "Cash"
    CREDIT_CARD = "CCard"
    INVESTMENT = "Invst"
    ASSET = "Oth A"
    LIABILITY = "Oth L"
    INVOICE = "Invoice"


class InvestmentAction(str, Enum):
    """Enum for investment transaction action types."""
    BUY = "Buy"
    BUY_X = "BuyX"
    SELL = "Sell"
    SELL_X = "SellX"
    DIV = "Div"
    DIV_X = "DivX"
    INT_INC = "IntInc"
    INT_INC_X = "IntIncX"
    REINV_DIV = "ReinvDiv"
    REINV_INT = "ReinvInt"
    REINV_LG = "ReinvLg"
    REINV_SH = "ReinvSh"
    CG_LONG = "CGLong"
    CG_SHORT = "CGShort"
    SHARES_IN = "ShrsIn"
    SHARES_OUT = "ShrsOut"
    XIN = "XIn"
    XOUT = "XOut"
    STOCK_SPLIT = "StkSplit"


class MemorizedTransactionType(str, Enum):
    """Enum for memorized transaction types."""
    CHECK = "KC"
    DEPOSIT = "KD"
    PAYMENT = "KP"
    INVESTMENT = "KI"
    ELECTRONIC = "KE"


class SplitTransaction(BaseModel):
    """Model for a split portion of a transaction."""
    category: str = Field(..., description="Category for split (S field)")
    memo: Optional[str] = Field(None, description="Memo for split (E field)")
    amount: float = Field(..., description="Amount for split ($ field)")
    percentage: Optional[float] = Field(None, description="Percentage for split (% field)")


class BaseTransaction(BaseModel):
    """Base model for all transaction types."""
    date: Optional[datetime] = Field(None, description="Transaction date (D field)")
    amount: Optional[float] = Field(None, description="Transaction amount (T field)")
    memo: Optional[str] = Field(None, description="Transaction memo (M field)")
    cleared_status: ClearedStatus = Field(ClearedStatus.UNCLEARED, description="Cleared status (C field)")
    
    @validator('date', pre=True)
    def parse_date(cls, value):
        """Parse various date formats into datetime object."""
        if value is None:
            return None
            
        if isinstance(value, datetime):
            return value
            
        if isinstance(value, str):
            # Try different date formats
            formats = [
                "%m/%d/%Y", "%m/%d/%y", "%d/%m/%Y", "%d/%m/%y", 
                "%Y-%m-%d", "%m-%d-%Y", "%d-%m-%Y"
            ]
            
            # Handle Quicken's format with apostrophe for year
            if "'" in value:
                parts = value.split("'")
                if len(parts) == 2:
                    prefix, year = parts
                    # Handle both 'YY and 'YYYY formats
                    if len(year) == 2:
                        century = "20" if int(year) < 50 else "19"
                        value = f"{prefix}{century}{year}"
                    else:
                        value = f"{prefix}{year}"
            
            for fmt in formats:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
                    
        raise ValueError(f"Invalid date format: {value}")


class BankingTransaction(BaseTransaction):
    """Model for banking, cash, credit card, and other non-investment transactions."""
    payee: Optional[str] = Field(None, description="Payee (P field)")
    number: Optional[str] = Field(None, description="Check or reference number (N field)")
    category: Optional[str] = Field(None, description="Category or transfer (L field)")
    address: Optional[List[str]] = Field(None, description="Address lines (A field)")
    splits: Optional[List[SplitTransaction]] = Field(None, description="Split parts of transaction")
    account: Optional[str] = Field(None, description="Account name this transaction belongs to")
    
    @validator('category')
    def validate_category(cls, value):
        """Validate and normalize category format."""
        if value is None:
            return value
            
        # Check if it's a transfer (enclosed in square brackets)
        if re.match(r"^\[.+\]$", value):
            return value
            
        # Validate category format (Category:Subcategory/Class)
        if ":" in value and "/" in value:
            parts = value.split("/")
            if len(parts) != 2:
                raise ValueError("Invalid category/class format")
        
        return value
    
    def is_transfer(self) -> bool:
        """Check if this transaction is a transfer to another account."""
        if self.category and re.match(r"^\[.+\]$", self.category):
            return True
        return False
    
    def get_transfer_account(self) -> Optional[str]:
        """Get the account name this transaction transfers to, if applicable."""
        if self.is_transfer():
            return self.category[1:-1]  # Remove the square brackets
        return None


class InvestmentTransaction(BaseTransaction):
    """Model for investment transactions."""
    action: InvestmentAction = Field(..., description="Investment action (N field)")
    security: Optional[str] = Field(None, description="Security name (Y field)")
    price: Optional[float] = Field(None, description="Price per share (I field)")
    quantity: Optional[float] = Field(None, description="Number of shares (Q field)")
    commission: Optional[float] = Field(None, description="Commission (O field)")
    account: Optional[str] = Field(None, description="Transfer account (L field)")
    category: Optional[str] = Field(None, description="Category (L field)")
    transfer_amount: Optional[float] = Field(None, description="Transfer amount ($ field)")
    payee: Optional[str] = Field(None, description="Text for transfers/reminders (P field)")


class CategoryItem(BaseModel):
    """Model for a category list item."""
    name: str = Field(..., description="Category name (N field)")
    description: Optional[str] = Field(None, description="Description (D field)")
    tax_related: bool = Field(False, description="Tax related flag (T field)")
    income: bool = Field(False, description="Income category (I field)")
    expense: bool = Field(True, description="Expense category (E field)")
    budget_amount: Optional[float] = Field(None, description="Budget amount (B field)")
    tax_schedule: Optional[str] = Field(None, description="Tax schedule info (R field)")


class ClassItem(BaseModel):
    """Model for a class list item."""
    name: str = Field(..., description="Class name (N field)")
    description: Optional[str] = Field(None, description="Description (D field)")


class AccountDefinition(BaseModel):
    """Model for an account definition."""
    name: str = Field(..., description="Account name (N field)")
    type: AccountType = Field(..., description="Account type (T field)")
    description: Optional[str] = Field(None, description="Description (D field)")
    credit_limit: Optional[float] = Field(None, description="Credit limit for credit cards (L field)")
    statement_balance_date: Optional[datetime] = Field(None, description="Statement date (/ field)")
    statement_balance: Optional[float] = Field(None, description="Statement balance ($ field)")


class MemorizedTransaction(BaseModel):
    """Model for a memorized transaction."""
    transaction_type: MemorizedTransactionType = Field(..., description="Transaction type (KC, KD, etc.)")
    amount: Optional[float] = Field(None, description="Amount (T field)")
    cleared_status: Optional[ClearedStatus] = Field(None, description="Cleared status (C field)")
    payee: Optional[str] = Field(None, description="Payee (P field)")
    memo: Optional[str] = Field(None, description="Memo (M field)")
    address: Optional[List[str]] = Field(None, description="Address (A field)")
    category: Optional[str] = Field(None, description="Category (L field)")
    splits: Optional[List[SplitTransaction]] = Field(None, description="Split categories")
    amortization: Optional[Dict[str, Union[str, float, int]]] = Field(None, description="Amortization fields (1-7)")


class QIFFile(BaseModel):
    """Model representing a complete QIF file with multiple accounts and transactions."""
    accounts: List[AccountDefinition] = Field(default_factory=list)
    bank_transactions: Dict[str, List[BankingTransaction]] = Field(default_factory=dict)
    cash_transactions: Dict[str, List[BankingTransaction]] = Field(default_factory=dict)
    credit_card_transactions: Dict[str, List[BankingTransaction]] = Field(default_factory=dict)
    investment_transactions: Dict[str, List[InvestmentTransaction]] = Field(default_factory=dict)
    asset_transactions: Dict[str, List[BankingTransaction]] = Field(default_factory=dict)
    liability_transactions: Dict[str, List[BankingTransaction]] = Field(default_factory=dict)
    categories: List[CategoryItem] = Field(default_factory=list)
    classes: List[ClassItem] = Field(default_factory=list)
    memorized_transactions: List[MemorizedTransaction] = Field(default_factory=list)
    
    def get_account_transactions(self, account_name: str) -> List[Union[BankingTransaction, InvestmentTransaction]]:
        """Get all transactions for a specific account."""
        all_transactions = []
        
        # Check each transaction type dictionary for this account
        for trans_dict in [
            self.bank_transactions,
            self.cash_transactions,
            self.credit_card_transactions,
            self.investment_transactions,
            self.asset_transactions,
            self.liability_transactions
        ]:
            if account_name in trans_dict:
                all_transactions.extend(trans_dict[account_name])
                
        # Sort transactions by date
        return sorted(all_transactions, key=lambda x: x.date)
    
    def add_transaction(self, account_name: str, account_type: AccountType, 
                        transaction: Union[BankingTransaction, InvestmentTransaction]) -> None:
        """Add a transaction to the appropriate account."""
        if account_type == AccountType.BANK:
            if account_name not in self.bank_transactions:
                self.bank_transactions[account_name] = []
            self.bank_transactions[account_name].append(transaction)
        elif account_type == AccountType.CASH:
            if account_name not in self.cash_transactions:
                self.cash_transactions[account_name] = []
            self.cash_transactions[account_name].append(transaction)
        elif account_type == AccountType.CREDIT_CARD:
            if account_name not in self.credit_card_transactions:
                self.credit_card_transactions[account_name] = []
            self.credit_card_transactions[account_name].append(transaction)
        elif account_type == AccountType.INVESTMENT:
            if account_name not in self.investment_transactions:
                self.investment_transactions[account_name] = []
            self.investment_transactions[account_name].append(transaction)
        elif account_type == AccountType.ASSET:
            if account_name not in self.asset_transactions:
                self.asset_transactions[account_name] = []
            self.asset_transactions[account_name].append(transaction)
        elif account_type == AccountType.LIABILITY:
            if account_name not in self.liability_transactions:
                self.liability_transactions[account_name] = []
            self.liability_transactions[account_name].append(transaction)


class CSVTemplate(BaseModel):
    """Model for CSV template definitions."""
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    account_type: AccountType = Field(..., description="Associated account type")
    delimiter: str = Field(",", description="CSV delimiter")
    has_header: bool = Field(True, description="Whether CSV has a header row")
    date_format: str = Field("%Y-%m-%d", description="Date format in the CSV")
    field_mapping: Dict[str, str] = Field(..., description="Mapping of CSV columns to QIF fields")
    skip_rows: int = Field(0, description="Number of rows to skip at beginning")
    amount_columns: List[str] = Field(default_factory=list, description="Columns to combine for amount")
    amount_multiplier: Optional[Dict[str, float]] = Field(None, description="Multipliers for amount columns")
    category_format: Optional[str] = Field(None, description="Format for category field")
    detect_transfers: bool = Field(True, description="Whether to detect transfers from category")
    transfer_pattern: str = Field(r"^\[(.+)\]$", description="Regex pattern to identify transfers")
