# QIF Implementation Guide

This guide provides detailed information for implementing the Quicken Interchange Format (QIF) in the CSV-QIF Converter application.

## 1. QIF File Structure

Each QIF file consists of:
1. A header line identifying the type of data
2. Multiple transaction blocks or entity entries
3. Each entry terminated with a caret (^) symbol

### 1.1 Basic Structure

```
!Type:[AccountType]
[Field Code][Value]
[Field Code][Value]
...
^
[Field Code][Value]
...
^
```

## 2. Account Types and Headers

| Header | Description | Usage |
|--------|-------------|-------|
| `!Type:Bank` | Banking transactions | For checking and savings accounts |
| `!Type:Cash` | Cash transactions | For cash flow tracking |
| `!Type:CCard` | Credit card transactions | For credit card accounts |
| `!Type:Invst` | Investment transactions | For investment and brokerage accounts |
| `!Type:Oth A` | Asset transactions | For tracking assets |
| `!Type:Oth L` | Liability transactions | For tracking liabilities |
| `!Account` | Account list or definition | For defining accounts |
| `!Type:Cat` | Category list | For defining categories |
| `!Type:Class` | Class list | For defining classes |
| `!Type:Memorized` | Memorized transaction list | For saved transaction templates |

## 3. Field Codes for Different Entity Types

### 3.1 Non-Investment Accounts (Bank, Cash, CCard, Oth A, Oth L)

| Code | Field | Description |
|------|-------|-------------|
| `D` | Date | Transaction date (MM/DD/YY or MM/DD/YYYY format) |
| `T` | Amount | Transaction amount (negative for payments) |
| `C` | Cleared status | Blank (uncleared), "*"/"c" (cleared), "X"/"R" (reconciled) |
| `N` | Number | Check number or reference |
| `P` | Payee | Payee or description |
| `M` | Memo | Additional information |
| `A` | Address | Up to 5 address lines + optional message |
| `L` | Category | Category/Subcategory/Transfer/Class format |
| `S` | Split category | Category for split portion |
| `E` | Split memo | Memo for split portion |
| `$` | Split amount | Amount for split portion |
| `%` | Split percent | Optional percentage for split |
| `F` | Reimbursable flag | Flag for reimbursable expense |

### 3.2 Investment Accounts

| Code | Field | Description |
|------|-------|-------------|
| `D` | Date | Transaction date |
| `N` | Action | Investment action code |
| `Y` | Security | Security name |
| `I` | Price | Price per share |
| `Q` | Quantity | Number of shares or split ratio |
| `T` | Amount | Transaction amount |
| `C` | Cleared status | Cleared flag |
| `P` | Text | First line text for transfers |
| `M` | Memo | Additional information |
| `O` | Commission | Commission cost |
| `L` | Account | Transfer account |
| `$` | Transfer amount | Amount transferred |

### 3.3 Account Information

| Code | Field | Description |
|------|-------|-------------|
| `N` | Name | Account name |
| `T` | Type | Account type |
| `D` | Description | Account description |
| `L` | Credit limit | Credit limit (credit cards only) |
| `/` | Statement date | Statement balance date |
| `$` | Statement balance | Statement balance amount |

### 3.4 Category List

| Code | Field | Description |
|------|-------|-------------|
| `N` | Category | Category name:subcategory name |
| `D` | Description | Category description |
| `T` | Tax related | Tax related flag |
| `I` | Income | Income category flag |
| `E` | Expense | Expense category flag |
| `B` | Budget | Budget amount |
| `R` | Tax schedule | Tax schedule information |

### 3.5 Class List

| Code | Field | Description |
|------|-------|-------------|
| `N` | Class | Class name |
| `D` | Description | Class description |

### 3.6 Memorized Transaction List

| Code | Field | Description |
|------|-------|-------------|
| `KC` | Check transaction | Transaction type |
| `KD` | Deposit transaction | Transaction type |
| `KP` | Payment transaction | Transaction type |
| `KI` | Investment transaction | Transaction type |
| `KE` | Electronic payee | Transaction type |
| (Other codes same as regular transactions) | | |

## 4. Investment Action Codes

| Action Code | Description |
|-------------|-------------|
| `Buy` | Buy security with cash in account |
| `BuyX` | Buy security with cash from another account |
| `Sell` | Sell security with proceeds in account |
| `SellX` | Sell security and transfer proceeds |
| `CGLong` | Long-term capital gains distribution |
| `CGShort` | Short-term capital gains distribution |
| `Div` | Dividend received in account |
| `DivX` | Dividend transferred to another account |
| `IntInc` | Interest income received |
| `ReinvDiv` | Dividend reinvested |
| `ShrsIn` | Add shares to account |
| `ShrsOut` | Remove shares from account |
| `StkSplit` | Stock split |
| `XIn` | Cash into account |
| `XOut` | Cash out of account |

## 5. Example QIF Files

### 5.1 Basic Banking Transaction

```
!Type:Bank
D03/15/2023
T-50.00
N1001
PGrocery Store
MFood for the week
LFood:Groceries
^
```

### 5.2 Split Transaction

```
!Type:Bank
D03/15/2023
T-100.00
PCostco
MMonthly shopping
LMiscellaneous
SFood:Groceries
E
$-60.00
SHousehold
ESupplies
$-40.00
^
```

### 5.3 Investment Transaction

```
!Type:Invst
D03/15/2023
NBuy
YAAPL
I150.00
Q10
T1500.00
MBought Apple stock
^
```

### 5.4 Category Definition

```
!Type:Cat
NFood:Groceries
DGrocery purchases
T
E
^
```

## 6. Implementation Notes

1. **Date Formats**: Support multiple date formats in import/export:
   - MM/DD/YY
   - MM/DD/YYYY
   - DD/MM/YY
   - DD/MM/YYYY
   - YYYY-MM-DD

2. **Amount Formatting**:
   - Negative amounts for payments (outflows)
   - Positive amounts for deposits (inflows)
   - Support for comma as thousand separator
   - Support for different decimal separators

3. **Split Transactions**:
   - Total of splits must equal the transaction total
   - Each split must have category (S) and amount ($)
   - Memo (E) is optional
   - Percentage (%) is optional

4. **Investment Transactions**:
   - Always use positive numbers for Q (Quantity) and T (Amount)
   - Action code (N) determines whether it's a buy or sell
   - Security name (Y) should match exactly across transactions

5. **Special Options**:
   - Support `!Option:AllXfr` to import all transfers
