from datetime import datetime
from typing import List, Optional, Union, Dict
from pydantic import BaseModel, Field
from .qif_models import QIFClearedStatus, InvestmentAction


class CSVBankTransaction(BaseModel):
    date: datetime = Field(..., description="Transaction date")
    amount: float = Field(..., description="Transaction amount")
    description: str = Field(..., description="Description or payee")
    reference: Optional[str] = Field(None, description="Reference number")
    memo: Optional[str] = Field(None, description="Additional information")
    category: Optional[str] = Field(None, description="Category/Subcategory/Transfer/Class")
    account_name: Optional[str] = Field(None, description="Account name for transfers")
    status: Optional[str] = Field(None, description="Cleared status")


class CSVInvestmentTransaction(BaseModel):
    date: datetime = Field(..., description="Transaction date")
    action: str = Field(..., description="Investment action")
    security: Optional[str] = Field(None, description="Security name")
    quantity: Optional[float] = Field(None, description="Number of shares")
    price: Optional[float] = Field(None, description="Price per share")
    amount: Optional[float] = Field(None, description="Transaction amount")
    commission: Optional[float] = Field(None, description="Commission cost")
    description: Optional[str] = Field(None, description="Description")
    category: Optional[str] = Field(None, description="Category")
    account: Optional[str] = Field(None, description="Account")
    memo: Optional[str] = Field(None, description="Additional information")
    status: Optional[str] = Field(None, description="Cleared status")


class CSVTemplate(BaseModel):
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    account_type: str = Field(..., description="Account type")
    field_mapping: Dict[str, str] = Field(..., description="Field mapping from CSV to QIF")
    date_format: str = Field("%Y-%m-%d", description="Date format")
    delimiter: str = Field(",", description="CSV delimiter")
