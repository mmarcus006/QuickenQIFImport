import pytest
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture
def test_data_dir():
    """Fixture for the test data directory."""
    return os.path.join(os.path.dirname(__file__), "data")

@pytest.fixture
def sample_bank_csv():
    """Fixture for a sample bank CSV content."""
    return """Date,Amount,Description,Reference,Notes,Category
2023-01-01,100.50,Grocery Store,123,Weekly groceries,Food:Groceries
2023-01-02,-50.25,Gas Station,,Fill up car,Auto:Fuel
2023-01-03,1200.00,Paycheck,DIRECT DEP,January salary,Income:Salary
"""

@pytest.fixture
def sample_investment_csv():
    """Fixture for a sample investment CSV content."""
    return """Date,Action,Security,Quantity,Price,Amount,Commission,Description,Memo,Category
2023-01-01,Buy,AAPL,10,150.75,-1507.50,7.50,Broker,Buy Apple stock,Investments:Stocks
2023-01-02,Sell,MSFT,5,250.25,1251.25,6.25,Broker,Sell Microsoft stock,Investments:Stocks
2023-01-03,Div,VTI,,,,0,Vanguard,Dividend payment,Income:Dividends
"""

@pytest.fixture
def sample_bank_qif():
    """Fixture for a sample bank QIF content."""
    return """!Type:Bank
D01/01/2023
T100.50
PGrocery Store
N123
MWeekly groceries
LFood:Groceries
^
D01/02/2023
T-50.25
PGas Station
MFill up car
LAuto:Fuel
^
D01/03/2023
T1200.00
PPaycheck
NDIRECT DEP
MJanuary salary
LIncome:Salary
^
"""

@pytest.fixture
def sample_investment_qif():
    """Fixture for a sample investment QIF content."""
    return """!Type:Invst
D01/01/2023
NBuy
YAAPL
Q10
I150.75
T-1507.50
O7.50
PBroker
MBuy Apple stock
LInvestments:Stocks
^
D01/02/2023
NSell
YMSFT
Q5
I250.25
T1251.25
O6.25
PBroker
MSell Microsoft stock
LInvestments:Stocks
^
D01/03/2023
NDiv
YVTI
T0
PVanguard
MDividend payment
LIncome:Dividends
^
"""
