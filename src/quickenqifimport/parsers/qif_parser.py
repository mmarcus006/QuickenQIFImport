from datetime import datetime
from typing import List, Dict, Optional, Union, TextIO, Tuple
import re
from ..models.qif_models import (
    QIFAccountType, QIFClearedStatus, InvestmentAction,
    BankTransaction, CashTransaction, CreditCardTransaction,
    AssetTransaction, LiabilityTransaction, InvestmentTransaction,
    Account, Category, Class, MemorizedTransaction, SplitTransaction,
    QIFFile
)


class QIFParser:
    def __init__(self):
        self.date_formats = [
            "%m/%d/%y", "%m/%d/%Y", "%d/%m/%y", "%d/%m/%Y", "%Y-%m-%d"
        ]

    def parse_file(self, file_path: str) -> QIFFile:
        """Parse a QIF file and return a QIFFile object."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return self.parse(file)

    def parse(self, file_content: Union[str, TextIO]) -> QIFFile:
        """Parse QIF content and return a QIFFile object."""
        if isinstance(file_content, str):
            lines = file_content.splitlines()
        else:
            lines = file_content.readlines()
            lines = [line.strip() for line in lines]

        if not lines:
            raise ValueError("Empty QIF content")

        header_line = lines[0].strip()
        if not header_line.startswith('!'):
            raise ValueError(f"Invalid QIF header: {header_line}")

        account_type = self._parse_header(header_line)
        qif_file = QIFFile(type=account_type)

        current_entries = []
        current_entry = []
        
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
                
            if line == '^':
                if current_entry:
                    current_entries.append(current_entry)
                    current_entry = []
            elif line.startswith('!'):
                if current_entries:
                    self._process_entries(qif_file, account_type, current_entries)
                    current_entries = []
                
                account_type = self._parse_header(line)
                qif_file.type = account_type
            else:
                current_entry.append(line)
        
        if current_entry:
            current_entries.append(current_entry)
        
        if current_entries:
            self._process_entries(qif_file, account_type, current_entries)
            
        return qif_file

    def _parse_header(self, header: str) -> QIFAccountType:
        """Parse the QIF header and return the account type."""
        header_map = {
            "!Type:Bank": QIFAccountType.BANK,
            "!Type:Cash": QIFAccountType.CASH,
            "!Type:CCard": QIFAccountType.CCARD,
            "!Type:Invst": QIFAccountType.INVESTMENT,
            "!Type:Oth A": QIFAccountType.ASSET,
            "!Type:Oth L": QIFAccountType.LIABILITY,
            "!Account": QIFAccountType.ACCOUNT,
            "!Type:Cat": QIFAccountType.CATEGORY,
            "!Type:Class": QIFAccountType.CLASS,
            "!Type:Memorized": QIFAccountType.MEMORIZED,
        }
        
        for key, value in header_map.items():
            if header.startswith(key):
                return value
                
        raise ValueError(f"Unknown QIF header: {header}")

    def _process_entries(self, qif_file: QIFFile, account_type: QIFAccountType, entries: List[List[str]]):
        """Process parsed entries and add them to the QIF file."""
        if account_type == QIFAccountType.BANK:
            if qif_file.bank_transactions is None:
                qif_file.bank_transactions = []
            for entry in entries:
                qif_file.bank_transactions.append(self._parse_bank_transaction(entry))
        elif account_type == QIFAccountType.CASH:
            if qif_file.cash_transactions is None:
                qif_file.cash_transactions = []
            for entry in entries:
                qif_file.cash_transactions.append(self._parse_cash_transaction(entry))
        elif account_type == QIFAccountType.CCARD:
            if qif_file.credit_card_transactions is None:
                qif_file.credit_card_transactions = []
            for entry in entries:
                qif_file.credit_card_transactions.append(self._parse_credit_card_transaction(entry))
        elif account_type == QIFAccountType.INVESTMENT:
            if qif_file.investment_transactions is None:
                qif_file.investment_transactions = []
            for entry in entries:
                qif_file.investment_transactions.append(self._parse_investment_transaction(entry))
        elif account_type == QIFAccountType.ASSET:
            if qif_file.asset_transactions is None:
                qif_file.asset_transactions = []
            for entry in entries:
                qif_file.asset_transactions.append(self._parse_asset_transaction(entry))
        elif account_type == QIFAccountType.LIABILITY:
            if qif_file.liability_transactions is None:
                qif_file.liability_transactions = []
            for entry in entries:
                qif_file.liability_transactions.append(self._parse_liability_transaction(entry))
        elif account_type == QIFAccountType.ACCOUNT:
            if qif_file.accounts is None:
                qif_file.accounts = []
            for entry in entries:
                qif_file.accounts.append(self._parse_account(entry))
        elif account_type == QIFAccountType.CATEGORY:
            if qif_file.categories is None:
                qif_file.categories = []
            for entry in entries:
                qif_file.categories.append(self._parse_category(entry))
        elif account_type == QIFAccountType.CLASS:
            if qif_file.classes is None:
                qif_file.classes = []
            for entry in entries:
                qif_file.classes.append(self._parse_class(entry))
        elif account_type == QIFAccountType.MEMORIZED:
            if qif_file.memorized_transactions is None:
                qif_file.memorized_transactions = []
            for entry in entries:
                qif_file.memorized_transactions.append(self._parse_memorized_transaction(entry))

    def _parse_date(self, date_str: str) -> datetime:
        """Parse a date string using various formats."""
        date_str = date_str.replace("'", "")
        
        for fmt in self.date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
                
        raise ValueError(f"Could not parse date: {date_str}")

    def _parse_amount(self, amount_str: str) -> float:
        """Parse an amount string to a float."""
        return float(amount_str.replace(',', ''))

    def _parse_cleared_status(self, status_str: str) -> QIFClearedStatus:
        """Parse a cleared status string to enum."""
        status_map = {
            "": QIFClearedStatus.UNCLEARED,
            "*": QIFClearedStatus.CLEARED,
            "c": QIFClearedStatus.CLEARED_ALT,
            "X": QIFClearedStatus.RECONCILED,
            "R": QIFClearedStatus.RECONCILED_ALT,
        }
        
        return status_map.get(status_str, QIFClearedStatus.UNCLEARED)

    def _create_field_dict(self, entry: List[str]) -> Dict[str, str]:
        """Convert QIF entry lines to a dictionary of fields."""
        field_dict = {}
        for line in entry:
            if line and len(line) > 1:
                field_code = line[0]
                field_value = line[1:]
                
                if field_code in field_dict:
                    if isinstance(field_dict[field_code], list):
                        field_dict[field_code].append(field_value)
                    else:
                        field_dict[field_code] = [field_dict[field_code], field_value]
                else:
                    field_dict[field_code] = field_value
                    
        return field_dict

    def _parse_bank_transaction(self, entry: List[str]) -> BankTransaction:
        """Parse a bank transaction entry."""
        field_dict = self._create_field_dict(entry)
        
        splits = self._extract_splits(field_dict)
        
        transaction = BankTransaction(
            date=self._parse_date(field_dict.get('D', '')),
            amount=self._parse_amount(field_dict.get('T', '0')),
            cleared_status=self._parse_cleared_status(field_dict.get('C', '')),
            number=field_dict.get('N'),
            payee=field_dict.get('P'),
            memo=field_dict.get('M'),
            address=field_dict.get('A', []) if isinstance(field_dict.get('A'), list) else [field_dict.get('A')] if field_dict.get('A') else None,
            category=field_dict.get('L'),
            splits=splits,
            reimbursable=True if field_dict.get('F') else None
        )
        
        return transaction

    def _parse_cash_transaction(self, entry: List[str]) -> CashTransaction:
        """Parse a cash transaction entry."""
        return CashTransaction(**self._parse_bank_transaction(entry).model_dump())

    def _parse_credit_card_transaction(self, entry: List[str]) -> CreditCardTransaction:
        """Parse a credit card transaction entry."""
        return CreditCardTransaction(**self._parse_bank_transaction(entry).model_dump())

    def _parse_asset_transaction(self, entry: List[str]) -> AssetTransaction:
        """Parse an asset transaction entry."""
        return AssetTransaction(**self._parse_bank_transaction(entry).model_dump())

    def _parse_liability_transaction(self, entry: List[str]) -> LiabilityTransaction:
        """Parse a liability transaction entry."""
        return LiabilityTransaction(**self._parse_bank_transaction(entry).model_dump())

    def _parse_investment_transaction(self, entry: List[str]) -> InvestmentTransaction:
        """Parse an investment transaction entry."""
        field_dict = self._create_field_dict(entry)
        
        action_str = field_dict.get('N', '')
        try:
            action = InvestmentAction(action_str)
        except ValueError:
            action = InvestmentAction.BUY  # Default
            
        transaction = InvestmentTransaction(
            date=self._parse_date(field_dict.get('D', '')),
            action=action,
            security=field_dict.get('Y'),
            price=float(field_dict.get('I', '0')) if field_dict.get('I') else None,
            quantity=float(field_dict.get('Q', '0')) if field_dict.get('Q') else None,
            amount=float(field_dict.get('T', '0')) if field_dict.get('T') else None,
            cleared_status=self._parse_cleared_status(field_dict.get('C', '')),
            text=field_dict.get('P'),
            memo=field_dict.get('M'),
            commission=float(field_dict.get('O', '0')) if field_dict.get('O') else None,
            account=field_dict.get('L'),
            transfer_amount=float(field_dict.get('$', '0')) if field_dict.get('$') else None
        )
        
        return transaction

    def _parse_account(self, entry: List[str]) -> Account:
        """Parse an account entry."""
        field_dict = self._create_field_dict(entry)
        
        account = Account(
            name=field_dict.get('N', ''),
            type=QIFAccountType(field_dict.get('T', 'Bank')),
            description=field_dict.get('D'),
            credit_limit=float(field_dict.get('L', '0')) if field_dict.get('L') else None,
            statement_date=self._parse_date(field_dict.get('/', '')) if field_dict.get('/') else None,
            statement_balance=float(field_dict.get('$', '0')) if field_dict.get('$') else None
        )
        
        return account

    def _parse_category(self, entry: List[str]) -> Category:
        """Parse a category entry."""
        field_dict = self._create_field_dict(entry)
        
        category = Category(
            name=field_dict.get('N', ''),
            description=field_dict.get('D'),
            tax_related=True if field_dict.get('T') else None,
            income=True if field_dict.get('I') else None,
            expense=True if field_dict.get('E') else None,
            budget_amount=float(field_dict.get('B', '0')) if field_dict.get('B') else None,
            tax_schedule=field_dict.get('R')
        )
        
        return category

    def _parse_class(self, entry: List[str]) -> Class:
        """Parse a class entry."""
        field_dict = self._create_field_dict(entry)
        
        cls = Class(
            name=field_dict.get('N', ''),
            description=field_dict.get('D')
        )
        
        return cls

    def _parse_memorized_transaction(self, entry: List[str]) -> MemorizedTransaction:
        """Parse a memorized transaction entry."""
        field_dict = self._create_field_dict(entry)
        
        transaction_type = ""
        for code in ['KC', 'KD', 'KP', 'KI', 'KE']:
            if code in field_dict:
                transaction_type = code
                break
                
        if transaction_type == 'KI':
            transaction = self._parse_investment_transaction(entry)
        else:
            transaction = self._parse_bank_transaction(entry)
            
        return MemorizedTransaction(
            transaction_type=transaction_type,
            transaction=transaction
        )

    def _extract_splits(self, field_dict: Dict[str, str]) -> Optional[List[SplitTransaction]]:
        """Extract split transactions from a field dictionary."""
        if 'S' not in field_dict:
            return None
            
        split_categories = field_dict.get('S', [])
        split_memos = field_dict.get('E', [])
        split_amounts = field_dict.get('$', [])
        split_percents = field_dict.get('%', [])
        
        if not isinstance(split_categories, list):
            split_categories = [split_categories]
        if not isinstance(split_memos, list):
            split_memos = [split_memos] if split_memos else []
        if not isinstance(split_amounts, list):
            split_amounts = [split_amounts]
        if not isinstance(split_percents, list):
            split_percents = [split_percents] if split_percents else []
            
        max_len = max(len(split_categories), len(split_amounts))
        split_memos = (split_memos + [None] * max_len)[:max_len]
        split_percents = (split_percents + [None] * max_len)[:max_len]
        
        splits = []
        for i in range(len(split_categories)):
            if i < len(split_amounts):
                memo = split_memos[i] if i < len(split_memos) else None
                percent = float(split_percents[i]) if i < len(split_percents) and split_percents[i] else None
                
                splits.append(SplitTransaction(
                    category=split_categories[i],
                    memo=memo,
                    amount=self._parse_amount(split_amounts[i]),
                    percent=percent
                ))
                
        return splits if splits else None
