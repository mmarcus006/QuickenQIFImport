from datetime import datetime
from enum import Enum
from typing import List, Optional, Union, Dict
from pydantic import BaseModel, Field


class QIFAccountType(str, Enum):
    BANK = "Bank"
    CASH = "Cash"
    CCARD = "CCard"
    INVESTMENT = "Invst"
    ASSET = "Oth A"
    LIABILITY = "Oth L"
    ACCOUNT = "Account"
    CATEGORY = "Cat"
    CLASS = "Class"
    MEMORIZED = "Memorized"


class QIFClearedStatus(str, Enum):
    UNCLEARED = ""
    CLEARED = "*"
    CLEARED_ALT = "c"
    RECONCILED = "X"
    RECONCILED_ALT = "R"


class InvestmentAction(str, Enum):
    BUY = "Buy"
    BUY_X = "BuyX"
    SELL = "Sell"
    SELL_X = "SellX"
    DIVIDEND = "Div"
    DIVIDEND_X = "DivX"
    REINVEST_DIV = "ReinvDiv"
    INTEREST_INCOME = "IntInc"
    LONG_TERM_CAP_GAIN = "CGLong"
    SHORT_TERM_CAP_GAIN = "CGShort"
    SHARES_IN = "ShrsIn"
    SHARES_OUT = "ShrsOut"
    STOCK_SPLIT = "StkSplit"
    CASH_IN = "XIn"
    CASH_OUT = "XOut"


class SplitTransaction(BaseModel):
    category: str = Field(..., description="Category for split portion")
    memo: Optional[str] = Field(None, description="Memo for split portion")
    amount: float = Field(..., description="Amount for split portion")
    percent: Optional[float] = Field(None, description="Optional percentage for split")


class BaseTransaction(BaseModel):
    date: datetime = Field(..., description="Transaction date")
    amount: float = Field(..., description="Transaction amount")
    cleared_status: Optional[QIFClearedStatus] = Field(None, description="Cleared status")
    number: Optional[str] = Field(None, description="Check number or reference")
    payee: Optional[str] = Field(None, description="Payee or description")
    memo: Optional[str] = Field(None, description="Additional information")
    address: Optional[List[str]] = Field(None, description="Address lines")
    category: Optional[str] = Field(None, description="Category/Subcategory/Transfer/Class")
    splits: Optional[List[SplitTransaction]] = Field(None, description="Split transactions")
    reimbursable: Optional[bool] = Field(None, description="Flag for reimbursable expense")


class BankTransaction(BaseTransaction):
    pass


class CashTransaction(BaseTransaction):
    pass


class CreditCardTransaction(BaseTransaction):
    pass


class AssetTransaction(BaseTransaction):
    pass


class LiabilityTransaction(BaseTransaction):
    pass


class InvestmentTransaction(BaseModel):
    date: datetime = Field(..., description="Transaction date")
    action: InvestmentAction = Field(..., description="Investment action code")
    security: Optional[str] = Field(None, description="Security name")
    price: Optional[float] = Field(None, description="Price per share")
    quantity: Optional[float] = Field(None, description="Number of shares or split ratio")
    amount: Optional[float] = Field(None, description="Transaction amount")
    cleared_status: Optional[QIFClearedStatus] = Field(None, description="Cleared flag")
    text: Optional[str] = Field(None, description="First line text for transfers")
    memo: Optional[str] = Field(None, description="Additional information")
    commission: Optional[float] = Field(None, description="Commission cost")
    account: Optional[str] = Field(None, description="Transfer account")
    transfer_amount: Optional[float] = Field(None, description="Amount transferred")


class Account(BaseModel):
    name: str = Field(..., description="Account name")
    type: QIFAccountType = Field(..., description="Account type")
    description: Optional[str] = Field(None, description="Account description")
    credit_limit: Optional[float] = Field(None, description="Credit limit (credit cards only)")
    statement_date: Optional[datetime] = Field(None, description="Statement balance date")
    statement_balance: Optional[float] = Field(None, description="Statement balance amount")


class Category(BaseModel):
    name: str = Field(..., description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    tax_related: Optional[bool] = Field(None, description="Tax related flag")
    income: Optional[bool] = Field(None, description="Income category flag")
    expense: Optional[bool] = Field(None, description="Expense category flag")
    budget_amount: Optional[float] = Field(None, description="Budget amount")
    tax_schedule: Optional[str] = Field(None, description="Tax schedule information")


class Class(BaseModel):
    name: str = Field(..., description="Class name")
    description: Optional[str] = Field(None, description="Class description")


class MemorizedTransaction(BaseModel):
    transaction_type: str = Field(..., description="Transaction type")
    transaction: Union[BaseTransaction, InvestmentTransaction] = Field(..., description="Transaction details")


class QIFFile(BaseModel):
    type: QIFAccountType = Field(..., description="QIF file type")
    bank_transactions: Optional[List[BankTransaction]] = Field(None, description="Bank transactions")
    cash_transactions: Optional[List[CashTransaction]] = Field(None, description="Cash transactions")
    credit_card_transactions: Optional[List[CreditCardTransaction]] = Field(None, description="Credit card transactions")
    investment_transactions: Optional[List[InvestmentTransaction]] = Field(None, description="Investment transactions")
    asset_transactions: Optional[List[AssetTransaction]] = Field(None, description="Asset transactions")
    liability_transactions: Optional[List[LiabilityTransaction]] = Field(None, description="Liability transactions")
    accounts: Optional[List[Account]] = Field(None, description="Accounts")
    categories: Optional[List[Category]] = Field(None, description="Categories")
    classes: Optional[List[Class]] = Field(None, description="Classes")
    memorized_transactions: Optional[List[MemorizedTransaction]] = Field(None, description="Memorized transactions")
