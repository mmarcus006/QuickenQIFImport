# Product Requirements Document: CSV-QIF Converter

## 1. Product Vision

Create a versatile and user-friendly desktop application that enables users to seamlessly convert financial transaction data between CSV templates and Quicken Interchange Format (QIF) files. The application will serve as a bridge between modern financial data exports and the QIF format, which remains important for personal financial management.

## 2. Target Users

- Personal finance enthusiasts who use multiple financial applications
- Accountants and bookkeepers who need to transfer data between systems
- Small business owners managing their own financial records
- Users of financial software that exports only CSV but need QIF compatibility

## 3. User Stories

1. **As a user**, I want to convert CSV files from my bank into QIF format, so I can import them into financial software that supports QIF.
2. **As a user**, I want to convert QIF files to CSV format, so I can analyze my financial data in spreadsheet applications.
3. **As a user**, I want to save and reuse CSV templates, so I don't have to remap fields for recurring imports.
4. **As a user**, I want to preview the conversion before finalizing it, so I can verify the data is mapped correctly.
5. **As a user**, I want to edit transactions during the conversion process, so I can correct any issues before finalizing.
6. **As a user**, I want to handle multiple account types (Bank, Credit Card, Investment, etc.), so I can manage all my financial data.
7. **As a user**, I want clear error messages when conversion issues occur, so I can take corrective action.

## 4. Functional Requirements

### 4.0 Entity Type Support

The application must support conversion for all QIF entity types:

#### 4.0.1 Transaction Types
- **Banking Transactions**: Checking, savings accounts with payee, amount, memo fields
- **Credit Card Transactions**: Similar to banking but with credit card-specific categorization
- **Cash Transactions**: For tracking cash flow
- **Investment Transactions**: For stocks, bonds, dividends with specialized fields
- **Asset & Liability Transactions**: For tracking property, loans, etc.
- **Transfer Transactions**: Special handling for transfers between accounts, with automatic detection when an account name appears in the category field in the format "[Account Name]"

#### 4.0.2 Non-Transaction Entities
- **Categories**: Hierarchical categories with income/expense designation
- **Classes**: For tracking by department, location, or project
- **Accounts**: Account definitions with type, description and settings
- **Memorized Transactions**: Saved transaction templates
- **Security Lists**: Investment security definitions

### 4.1 CSV to QIF Conversion

- Support for all QIF account types with proper headers:
  - `!Type:Bank` - Bank account transactions
  - `!Type:Cash` - Cash account transactions
  - `!Type:CCard` - Credit card account transactions
  - `!Type:Invst` - Investment account transactions
  - `!Type:Oth A` - Asset account transactions
  - `!Type:Oth L` - Liability account transactions
  - `!Account` - Account list or which account follows
  - `!Type:Cat` - Category list
  - `!Type:Class` - Class list
  - `!Type:Memorized` - Memorized transaction list
- Field mapping interface to match CSV columns to QIF fields
- Support for converting split transactions
- Date format specification and conversion
- Handling of special characters and text encoding

### 4.2 QIF to CSV Conversion

- Extract all transaction data from QIF files
- Generate properly formatted CSV with headers
- Preserve split transaction information
- Maintain category and sub-category relationships
- Preserve memos and notes
- Support conversion of all QIF entity types:
  - Regular transactions (banking, credit card, cash, etc.)
  - Investment transactions with security information
  - Category lists with descriptions and tax information
  - Class lists
  - Memorized transaction lists
  - Account information

### 4.3 Template Management

- Save and load CSV mapping templates
- Auto-detection of CSV format based on headers or patterns
- Template sharing functionality
- Built-in predefined templates for common financial institutions including:
  - Bank transaction templates (Chase, Bank of America, Wells Fargo, etc.)
  - Credit card transaction templates (Visa, Mastercard, American Express, etc.)
  - Investment transaction templates (Vanguard, Fidelity, Charles Schwab, etc.)
  - Custom template creation with visual mapping interface
- Template version control and update mechanism

### 4.4 Transaction Editing

- Grid view of transactions for review before conversion
- Edit capabilities for individual transaction fields
- Bulk edit functionality for multiple transactions
- Transaction filtering and sorting
- Split transaction editing interface

### 4.5 Account Type Support

- Banking accounts (checking, savings)
- Credit card accounts
- Investment accounts
- Cash accounts
- Asset and liability accounts
- Category lists
- Memorized transaction lists

## 5. Non-Functional Requirements

### 5.1 Performance

- Handle files with up to 10,000 transactions without significant delay
- Complete typical conversions in under 5 seconds
- UI remains responsive during conversion processes

### 5.2 User Interface and Experience

- Modern GUI with contemporary design elements following Material Design or Fluent Design principles
- Color scheme with primary, secondary, and accent colors that support both light and dark modes
- Responsive layout that adjusts to different screen sizes and resolutions
- Custom-designed icons for primary actions
- Animated transitions for improved user experience
- Consistent visual hierarchy across all screens
- High contrast mode for accessibility
- Drag-and-drop functionality for file handling
- Visual confirmation for successful operations

### 5.3 Usability

- Intuitive interface with minimal learning curve
- Comprehensive tooltips and help documentation
- Keyboard shortcuts for power users
- Consistent feedback during operations

### 5.3 Reliability

- Data validation to ensure QIF format integrity
- Error handling with clear user notifications
- Auto-save of work in progress to prevent data loss
- Transaction log for troubleshooting

### 5.4 Security

- No data sent to external servers
- All processing done locally
- Optional password protection for templates containing sensitive mapping information

## 6. Technical Specifications

### 6.1 Architecture

- Object-oriented programming approach with clear separation of concerns
- Core conversion engine independent from UI layer
- Modular design for extensibility
- MVC (Model-View-Controller) or MVVM (Model-View-ViewModel) architecture

### 6.2 Data Models

- Utilize Pydantic models for data validation and serialization
- Define comprehensive models for all QIF entity types:
  - Transaction models (Banking, Investment, etc.)
  - Account models
  - Category models
  - Class models
  - Security models
  - Template models
- Implement inheritance hierarchy where appropriate
- Ensure type safety with comprehensive type annotations

### 6.3 Code Quality

- Implement DRY (Don't Repeat Yourself) principles
- Follow SOLID principles
- Comprehensive error handling
- Type hinting throughout codebase
- Automated testing with pytest
  - Unit tests for all core functionality
  - Integration tests for conversion pipelines
  - UI tests for critical user workflows
  - Minimum 85% code coverage
- Continuous integration setup with GitHub Actions

### 6.3 File Handling

- Support for various CSV delimiters (comma, tab, semicolon)
- UTF-8 encoding support
- Large file handling with streaming approach
- Drag and drop file interface

### 6.4 QIF Format Compliance

- Strict adherence to QIF format specifications
- Support for all transaction field indicators:
  - Non-Investment accounts: D (Date), T (Amount), C (Cleared status), N (Num), P (Payee), M (Memo), L (Category), etc.
  - Investment accounts: D (Date), N (Action), Y (Security), I (Price), Q (Quantity), T (Transaction amount), etc.
  - Split transactions: S (Category in split), E (Memo in split), $ (Dollar amount of split)
  - Account information: N (Name), T (Type), D (Description), etc.
  - Categories: N (Category), D (Description), T (Tax related), I (Income category), etc.
  - Memorized transactions: T (Amount), P (Payee), M (Memo), etc.
- Proper handling of transaction end markers (^)
- Account type header compliance
- Support for the `!Option:AllXfr` option (imports all transfers regardless of settings)

## 7. User Interface Requirements

### 7.1 Layout

- Clean, modern interface with intuitive navigation
- Main workflow: Select operation → Upload file → Map fields → Preview → Edit → Convert
- Transaction grid view with filtering capabilities
- Split pane view to compare source and target formats

### 7.2 Features

- Dark/light mode toggle
- Resizable panels and windows
- Transaction search functionality
- Progress indicators for lengthy operations
- Field mapping visualization

### 7.3 Accessibility

- Keyboard navigation support
- Screen reader compatibility
- Configurable font sizes
- High contrast mode

## 8. Future Enhancements (Version 2.0)

- Integration with common financial software via API
- Batch processing of multiple files
- Custom rule creation for transaction categorization
- Advanced filtering and reporting capabilities
- Cloud template storage and sharing

## 9. Success Metrics

- Successful conversion rate (>99% of transactions correctly converted)
- User satisfaction with interface (measured through feedback)
- Time saved compared to manual data entry or alternative methods
- Number of account types successfully supported
