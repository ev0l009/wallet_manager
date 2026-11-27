# 3. Assumptions

### ASM-01: Single-User Execution Environment

- The system assumes an isolated, local execution architecture dedicated to a single user profile.
- Remote user authentication, role-based access controls (RBAC), and session tokens are outside the current design scope.

### ASM-02: Ex Post Facto Ledger Recording

- All manually entered financial records are assumed to represent transactions that have already concluded in the real world.
- This assumption justifies the rejection of future-dated transactions.

### ASM-03: Single-Threaded Execution and File Access

- The system assumes synchronous, single-threaded execution by one terminal process at a time.
- Concurrent file access, multi-process write conflicts, and race conditions are outside the supported execution model.
- The application does not guarantee multi-process concurrency control.

### ASM-04: Environment and Runtime Compatibility

- The application assumes execution within a standard command-line interface terminal.
- Python 3.10 or higher must be installed on the host operating system.

### ASM-05: Controllable System Date Provider

- The application must obtain the current calendar date through a dedicated date-provider function rather than directly accessing the system clock throughout the Business Logic Layer.
- During normal execution, the provider must return the host operating system's current local calendar date.
- The date provider must be replaceable or injectable during automated testing.
- All future-date validation must use the date returned by this provider to ensure consistent and reproducible results.

### ASM-06: Controlled Application Configuration

- The application assumes that supported account types, transaction classifications, and expense categories are centrally defined.
- Supported transaction classifications are `INCOME`, `EXPENSE`, and `TRANSFER`.
- Configuration changes must be made through controlled application updates rather than arbitrary user modifications to the JSON storage file.
- Existing historical transaction records must remain readable following compatible configuration updates.

### ASM-07: Ledger-Derived Account Balances

- The system assumes that account balances are derived exclusively from associated historical transaction records.
- Account entities do not maintain independently stored or cached balance attributes.
- Newly created accounts contain no financial balance data and have a ledger-derived balance of zero Kobo until associated transactions are recorded.
- All balance-dependent operations must obtain balances from the transaction ledger.

### ASM-08: Compensating Transaction Corrections

- The system assumes that incorrectly recorded financial transactions will be counteracted through new ordinary transactions rather than dedicated reversal records.
- Counteracting transactions must retain their normal transaction classifications (`INCOME`, `EXPENSE`, or `TRANSFER`).
- `INCOME` transactions are counteracted through `EXPENSE` transactions.
- `EXPENSE` transactions are counteracted through `INCOME` transactions.
- `TRANSFER` transactions are counteracted through `TRANSFER` transactions in the opposite direction.
- Users are responsible for providing descriptive context identifying the purpose of counteracting transactions.
- The original and counteracting transactions must remain independently identifiable in the historical ledger.

# 4. Identified Ambiguities

### AMB-01: Terminal Interaction Pattern

- **Ambiguity:** The original requirements define functional capabilities but do not specify how users should interact with the application through the CLI.
- **Resolution:** The application will use a synchronous interactive menu loop implemented with Python's native `input()` utility rather than raw command-line argument parsing.

### AMB-02: Case Sensitivity for Account-Name Uniqueness

- **Ambiguity:** The original requirements require unique account names but do not define how capitalization should affect uniqueness.
- **Resolution:** Account-name uniqueness will be evaluated case-insensitively across both active and inactive accounts.
- **Example:** "Cash" and "cash" will be treated as duplicate account names.
- Leading and trailing whitespace will be removed before uniqueness evaluation.
- Renaming and reactivation will enforce the same uniqueness rule.

### AMB-03: Persistence Technology Selection

- **Ambiguity:** The original requirements specify persistent transaction history but do not prescribe a storage technology.
- **Resolution:** The application will use a structured JSON flat-file as its exclusive persistence mechanism. SQLite and other database management systems are excluded from the current implementation.

**Justification:**

JSON provides a lightweight, human-readable persistence mechanism suitable for the application's single-user, single-process execution environment. It integrates directly with Python's native `json` module and supports the established Data Access Layer architecture.

**Trade-off:**

JSON does not provide native database indexing, query optimization, transactional rollback, or database-level concurrency controls. Consequently, large transaction histories will increase file parsing, serialization, filtering, and pagination costs.

### AMB-04: Transaction Category and Description Semantics

- **Ambiguity:** The requirements distinguish descriptive labels from expense categories but do not explicitly define how these fields apply to each transaction type.
- **Resolution:**
  - `EXPENSE` transactions must contain a valid expense category and may contain a descriptive label.
  - `INCOME` transactions may contain a descriptive label but must not contain an expense category.
  - `TRANSFER` transactions may contain a descriptive label but must not contain an expense category.
  - Counteracting transactions must follow the metadata requirements of their ordinary transaction classifications.
  - The description field may contain contextual information identifying a transaction as a correction or explaining why it was recorded.
- The category field must be `null` for `INCOME` and `TRANSFER` records.
- The category field must not be used to classify internal transfers or counteracting transactions.

### AMB-05: Account Balance Initialization

- **Ambiguity:** The original requirements do not explicitly distinguish between an account's initial financial state and the existence of a stored account balance attribute.
- **Resolution:**
  - Newly created accounts must not contain an assigned or stored balance attribute.
  - An account with no associated transactions must have a ledger-derived balance of zero Kobo.
  - Initial funding must be recorded through a valid `INCOME` transaction rather than directly assigning a starting balance.
  - This preserves the transaction ledger as the sole authoritative source of account balances.

### AMB-06: Transaction Correction Mechanism

- **Ambiguity:** The original requirements establish an immutable transaction ledger but do not specify how users recover from incorrectly recorded transactions.
- **Resolution:**
  - Historical transactions must never be directly edited or deleted through normal application operations.
  - Incorrect transactions must be counteracted through new ordinary transactions that produce the opposite financial effect.
  - An incorrectly recorded `INCOME` transaction must be counteracted through an `EXPENSE` transaction.
  - An incorrectly recorded `EXPENSE` transaction must be counteracted through an `INCOME` transaction.
  - Counteracting transactions must not introduce a dedicated `REVERSAL` classification or special transaction relationship.
  - Users may subsequently record replacement transactions containing the correct information.
  - Original and counteracting transactions must remain independently identifiable in the historical ledger.
  - Descriptive labels may be used to explain the relationship between an incorrect transaction and its counteracting transaction.

### AMB-07: Architecture Dependency Direction

- **Ambiguity:** The original architecture describes communication between the Business Logic and Data Access Layers without defining dependency ownership.
- **Resolution:** The application will use one-way runtime interaction:
  - Presentation Layer calls the Business Logic Layer.
  - Business Logic Layer directly imports and uses the persistence operations provided by the Data Access Layer.
  - Data Access Layer handles JSON file operations independently of business workflows.
  - The application entry point initializes and connects the application components.
- The Data Access Layer must not import or depend on the Business Logic Layer or Presentation Layer.
- The Business Logic Layer must not perform direct filesystem operations.
- The Presentation Layer must not access the Data Access Layer directly.
- The Data Access Layer must remain responsible for JSON serialization, deserialization, and persistence operations.
- Business operations must remain testable independently of terminal interaction. Persistence tests must use controlled JSON file paths or temporary JSON files through the concrete Data Access Layer.
- No abstract storage interface or alternative storage implementation mechanism is required.

---