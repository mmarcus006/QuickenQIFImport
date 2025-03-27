from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QComboBox, QLineEdit, QTableView, QDialog,
    QGroupBox, QRadioButton, QDateEdit, QDoubleSpinBox,
    QCheckBox, QSpinBox, QMessageBox, QDialogButtonBox,
    QFormLayout, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QStandardItemModel, QStandardItem

from ...models.models import (
    BaseTransaction, BankingTransaction, InvestmentTransaction,
    SplitTransaction, AccountType
)
from datetime import datetime

class TransactionEditor(QDialog):
    """Dialog for editing transactions."""
    
    transaction_saved = pyqtSignal(BaseTransaction)
    
    def __init__(self, transaction=None, account_type=AccountType.BANK, parent=None):
        """Initialize the transaction editor.
        
        Args:
            transaction: Transaction to edit (or None for a new transaction)
            account_type: Type of account for the transaction
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.transaction = transaction
        self.account_type = account_type
        self.is_new = transaction is None
        
        self.setWindowTitle("Edit Transaction" if not self.is_new else "New Transaction")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        self._create_ui()
        
        if transaction:
            self._load_transaction()
    
    def _create_ui(self):
        """Create the UI components."""
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        if self.account_type == AccountType.INVESTMENT:
            self._create_investment_tab()
        else:
            self._create_banking_tab()
        
        if self.account_type != AccountType.INVESTMENT:
            self._create_split_tab()
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | 
            QDialogButtonBox.StandardButton.Cancel
        )
        main_layout.addWidget(button_box)
        
        button_box.accepted.connect(self._on_save)
        button_box.rejected.connect(self.reject)
    
    def _create_banking_tab(self):
        """Create the banking transaction tab."""
        tab = QWidget()
        layout = QFormLayout()
        tab.setLayout(layout)
        
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(-1000000, 1000000)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setSingleStep(1.0)
        self.amount_spin.setPrefix("$ ")
        
        self.payee_edit = QLineEdit()
        self.number_edit = QLineEdit()
        self.memo_edit = QLineEdit()
        self.category_edit = QLineEdit()
        self.account_edit = QLineEdit()
        
        self.cleared_combo = QComboBox()
        self.cleared_combo.addItems(["Not Cleared", "Cleared", "Reconciled"])
        
        layout.addRow("Date:", self.date_edit)
        layout.addRow("Amount:", self.amount_spin)
        layout.addRow("Payee:", self.payee_edit)
        layout.addRow("Number:", self.number_edit)
        layout.addRow("Memo:", self.memo_edit)
        layout.addRow("Category:", self.category_edit)
        layout.addRow("Account:", self.account_edit)
        layout.addRow("Status:", self.cleared_combo)
        
        self.tab_widget.addTab(tab, "Transaction")
    
    def _create_investment_tab(self):
        """Create the investment transaction tab."""
        tab = QWidget()
        layout = QFormLayout()
        tab.setLayout(layout)
        
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        
        self.action_combo = QComboBox()
        self.action_combo.addItems([
            "Buy", "Sell", "Div", "IntInc", "ReinvDiv", "ShrsIn", "ShrsOut",
            "StkSplit", "CGLong", "CGShort"
        ])
        
        self.security_edit = QLineEdit()
        
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setRange(-1000000, 1000000)
        self.quantity_spin.setDecimals(6)
        self.quantity_spin.setSingleStep(1.0)
        
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 1000000)
        self.price_spin.setDecimals(6)
        self.price_spin.setSingleStep(1.0)
        self.price_spin.setPrefix("$ ")
        
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(-1000000, 1000000)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setSingleStep(1.0)
        self.amount_spin.setPrefix("$ ")
        
        self.commission_spin = QDoubleSpinBox()
        self.commission_spin.setRange(0, 1000000)
        self.commission_spin.setDecimals(2)
        self.commission_spin.setSingleStep(1.0)
        self.commission_spin.setPrefix("$ ")
        
        self.payee_edit = QLineEdit()
        self.memo_edit = QLineEdit()
        self.category_edit = QLineEdit()
        self.account_edit = QLineEdit()
        
        self.cleared_combo = QComboBox()
        self.cleared_combo.addItems(["Not Cleared", "Cleared", "Reconciled"])
        
        layout.addRow("Date:", self.date_edit)
        layout.addRow("Action:", self.action_combo)
        layout.addRow("Security:", self.security_edit)
        layout.addRow("Quantity:", self.quantity_spin)
        layout.addRow("Price:", self.price_spin)
        layout.addRow("Amount:", self.amount_spin)
        layout.addRow("Commission:", self.commission_spin)
        layout.addRow("Payee:", self.payee_edit)
        layout.addRow("Memo:", self.memo_edit)
        layout.addRow("Category:", self.category_edit)
        layout.addRow("Account:", self.account_edit)
        layout.addRow("Status:", self.cleared_combo)
        
        self.tab_widget.addTab(tab, "Transaction")
        
        self.action_combo.currentIndexChanged.connect(self._on_action_changed)
        self.quantity_spin.valueChanged.connect(self._on_quantity_or_price_changed)
        self.price_spin.valueChanged.connect(self._on_quantity_or_price_changed)
    
    def _create_split_tab(self):
        """Create the split transaction tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        self.split_table = QTableView()
        self.split_model = QStandardItemModel()
        self.split_model.setHorizontalHeaderLabels(["Category", "Memo", "Amount"])
        self.split_table.setModel(self.split_model)
        
        button_layout = QHBoxLayout()
        self.add_split_button = QPushButton("Add Split")
        self.remove_split_button = QPushButton("Remove Split")
        
        button_layout.addWidget(self.add_split_button)
        button_layout.addWidget(self.remove_split_button)
        button_layout.addStretch()
        
        layout.addWidget(self.split_table)
        layout.addLayout(button_layout)
        
        self.tab_widget.addTab(tab, "Split")
        
        self.add_split_button.clicked.connect(self._on_add_split)
        self.remove_split_button.clicked.connect(self._on_remove_split)
    
    def _load_transaction(self):
        """Load transaction data into the form."""
        if self.transaction.date:
            self.date_edit.setDate(QDate(
                self.transaction.date.year,
                self.transaction.date.month,
                self.transaction.date.day
            ))
        
        if self.transaction.amount is not None:
            self.amount_spin.setValue(self.transaction.amount)
        
        if hasattr(self.transaction, 'payee') and self.transaction.payee:
            self.payee_edit.setText(self.transaction.payee)
        
        if hasattr(self.transaction, 'memo') and self.transaction.memo:
            self.memo_edit.setText(self.transaction.memo)
        
        if hasattr(self.transaction, 'category') and self.transaction.category:
            self.category_edit.setText(self.transaction.category)
        
        if hasattr(self.transaction, 'account') and self.transaction.account:
            self.account_edit.setText(self.transaction.account)
        
        if hasattr(self.transaction, 'cleared_status') and self.transaction.cleared_status:
            if self.transaction.cleared_status == 'X':
                self.cleared_combo.setCurrentIndex(1)  # Cleared
            elif self.transaction.cleared_status == '*':
                self.cleared_combo.setCurrentIndex(2)  # Reconciled
            else:
                self.cleared_combo.setCurrentIndex(0)  # Not Cleared
        
        if isinstance(self.transaction, BankingTransaction):
            if hasattr(self.transaction, 'number') and self.transaction.number:
                self.number_edit.setText(self.transaction.number)
            
            if hasattr(self.transaction, 'splits') and self.transaction.splits:
                for split in self.transaction.splits:
                    category_item = QStandardItem(split.category or "")
                    memo_item = QStandardItem(split.memo or "")
                    amount_item = QStandardItem(f"{split.amount:.2f}" if split.amount is not None else "")
                    
                    self.split_model.appendRow([category_item, memo_item, amount_item])
        
        elif isinstance(self.transaction, InvestmentTransaction):
            if hasattr(self.transaction, 'action') and self.transaction.action:
                action_index = self.action_combo.findText(self.transaction.action)
                if action_index >= 0:
                    self.action_combo.setCurrentIndex(action_index)
            
            if hasattr(self.transaction, 'security') and self.transaction.security:
                self.security_edit.setText(self.transaction.security)
            
            if hasattr(self.transaction, 'quantity') and self.transaction.quantity is not None:
                self.quantity_spin.setValue(self.transaction.quantity)
            
            if hasattr(self.transaction, 'price') and self.transaction.price is not None:
                self.price_spin.setValue(self.transaction.price)
            
            if hasattr(self.transaction, 'commission') and self.transaction.commission is not None:
                self.commission_spin.setValue(self.transaction.commission)
    
    def _on_action_changed(self, index):
        """Handle action selection changed event.
        
        Args:
            index: Selected index
        """
        action = self.action_combo.currentText()
        
        if action in ["Buy", "Sell"]:
            self.quantity_spin.setEnabled(True)
            self.price_spin.setEnabled(True)
            self.commission_spin.setEnabled(True)
        elif action in ["Div", "IntInc", "CGLong", "CGShort"]:
            self.quantity_spin.setEnabled(False)
            self.price_spin.setEnabled(False)
            self.commission_spin.setEnabled(False)
        elif action in ["ReinvDiv"]:
            self.quantity_spin.setEnabled(True)
            self.price_spin.setEnabled(True)
            self.commission_spin.setEnabled(False)
        elif action in ["ShrsIn", "ShrsOut"]:
            self.quantity_spin.setEnabled(True)
            self.price_spin.setEnabled(False)
            self.commission_spin.setEnabled(False)
        elif action in ["StkSplit"]:
            self.quantity_spin.setEnabled(True)
            self.price_spin.setEnabled(False)
            self.commission_spin.setEnabled(False)
    
    def _on_quantity_or_price_changed(self, value):
        """Handle quantity or price changed event.
        
        Args:
            value: New value
        """
        action = self.action_combo.currentText()
        
        if action in ["Buy", "Sell", "ReinvDiv"]:
            quantity = self.quantity_spin.value()
            price = self.price_spin.value()
            commission = self.commission_spin.value() if action in ["Buy", "Sell"] else 0.0
            
            amount = quantity * price
            
            if action == "Buy":
                amount = -abs(amount) - commission
            elif action == "Sell":
                amount = abs(amount) - commission
            
            self.amount_spin.setValue(amount)
    
    def _on_add_split(self):
        """Handle add split button click event."""
        category_item = QStandardItem("")
        memo_item = QStandardItem("")
        amount_item = QStandardItem("")
        
        self.split_model.appendRow([category_item, memo_item, amount_item])
    
    def _on_remove_split(self):
        """Handle remove split button click event."""
        selected_indexes = self.split_table.selectedIndexes()
        
        if selected_indexes:
            row = selected_indexes[0].row()
            
            self.split_model.removeRow(row)
    
    def _on_save(self):
        """Handle save button click event."""
        try:
            if self.account_type == AccountType.INVESTMENT:
                transaction = self._create_investment_transaction()
            else:
                transaction = self._create_banking_transaction()
            
            self.transaction_saved.emit(transaction)
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save transaction: {str(e)}")
    
    def _create_banking_transaction(self):
        """Create a banking transaction from form data.
        
        Returns:
            BankingTransaction: Created transaction
        """
        date_value = self.date_edit.date().toPyDate()
        amount_value = self.amount_spin.value()
        payee_value = self.payee_edit.text()
        number_value = self.number_edit.text()
        memo_value = self.memo_edit.text()
        category_value = self.category_edit.text()
        account_value = self.account_edit.text()
        
        cleared_index = self.cleared_combo.currentIndex()
        cleared_value = None
        if cleared_index == 1:
            cleared_value = 'X'  # Cleared
        elif cleared_index == 2:
            cleared_value = '*'  # Reconciled
        
        transaction = BankingTransaction(
            date=date_value,
            amount=amount_value,
            payee=payee_value,
            number=number_value,
            memo=memo_value,
            category=category_value,
            account=account_value,
            cleared_status=cleared_value,
            splits=[]
        )
        
        for row in range(self.split_model.rowCount()):
            category_item = self.split_model.item(row, 0)
            memo_item = self.split_model.item(row, 1)
            amount_item = self.split_model.item(row, 2)
            
            if category_item and amount_item:
                category = category_item.text()
                memo = memo_item.text() if memo_item else None
                
                try:
                    amount = float(amount_item.text())
                except ValueError:
                    amount = 0.0
                
                split = SplitTransaction(
                    category=category,
                    amount=amount,
                    memo=memo
                )
                
                transaction.splits.append(split)
        
        return transaction
    
    def _create_investment_transaction(self):
        """Create an investment transaction from form data.
        
        Returns:
            InvestmentTransaction: Created transaction
        """
        date_value = self.date_edit.date().toPyDate()
        action_value = self.action_combo.currentText()
        security_value = self.security_edit.text()
        quantity_value = self.quantity_spin.value()
        price_value = self.price_spin.value()
        amount_value = self.amount_spin.value()
        commission_value = self.commission_spin.value()
        payee_value = self.payee_edit.text()
        memo_value = self.memo_edit.text()
        category_value = self.category_edit.text()
        account_value = self.account_edit.text()
        
        cleared_index = self.cleared_combo.currentIndex()
        cleared_value = None
        if cleared_index == 1:
            cleared_value = 'X'  # Cleared
        elif cleared_index == 2:
            cleared_value = '*'  # Reconciled
        
        transaction = InvestmentTransaction(
            date=date_value,
            action=action_value,
            security=security_value,
            quantity=quantity_value if quantity_value != 0 else None,
            price=price_value if price_value != 0 else None,
            amount=amount_value,
            commission=commission_value if commission_value != 0 else None,
            payee=payee_value,
            memo=memo_value,
            category=category_value,
            account=account_value,
            cleared_status=cleared_value
        )
        
        return transaction
