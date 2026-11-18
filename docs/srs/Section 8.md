# 8.0 Testing Strategy

To guarantee system stability, mathematical integrity, and compliance with the defined business rules, the application must implement a multi-tiered automated testing suite using Python's built-in `unittest` framework.

Testing must cover:

- **Happy Paths:** Valid inputs and successful operations.
- **Failure Paths:** Invalid data and rejected operations.
- **Boundary Edge Cases:** Values at or near defined constraints.
- **Domain Invariants:** Mathematical and structural properties that must always remain true.
- **Persistence Integrity:** Successful and unsuccessful file operations.
- **Restart Persistence:** Recovery of previously committed state after application reinitialization.
- **Cross-Layer Integration:** Communication between application tiers.
- **End-to-End Workflows:** Complete user interactions through the CLI.

## 8.1 Unit Testing (Isolated Functional Integrity)

Unit tests must isolate specific business functions and validation mechanisms.

External dependencies, particularly physical disk operations and date providers, must be replaced with controlled test doubles where appropriate.

The Business Logic Layer must depend on an abstract storage interface so that unit tests can use an in-memory fake storage implementation.

Unit tests must not require access to the actual JSON storage file.

**Example unit test coverage:**

| Targeted Module | Strategy | Test Function Identifier | Test Parameters / Inputs | Expected Terminal State / Exception |
| --- | --- | --- | --- | --- |
| Account Creation | Happy Path | `test_create_account_success` | name="Polaris Bank", type="BANK" | Account receives an automatically generated ID, zero Kobo, and ACTIVE status. |
| Account Creation | Failure Path | `test_create_account_name_too_short` | name="Pol", type="BANK" | Raises `InvalidAccountNameError`. |
| Account Creation | Edge Case | `test_create_account_exact_lower_bound` | name="Opay", type="MOBILE\_WALLET" | Account initialized successfully. |
| Account Creation | Failure Path | `test_duplicate_account_name_case_insensitive` | Existing name="Cash"; new name="cash" | Raises `DuplicateAccountNameError`. |
| Account Creation | Failure Path | `test_duplicate_name_inactive_account` | Existing inactive account name="Cash"; new name="Cash" | Raises `DuplicateAccountNameError`. |
| Account Creation | Happy Path | `test_account_constructor_generates_id` | name="First Bank", type="BANK" | ID is generated internally. |
| Account Creation | Happy Path | `test_new_account_starts_with_zero_balance` | Valid account creation. | Initial balance equals zero Kobo. |
| Account Lifecycle | Happy Path | `test_rename_account_success` | Rename existing account to an unused valid name. | Name updated without changing account ID or historical references. |
| Account Lifecycle | Failure Path | `test_rename_account_duplicate_name` | Rename account to another existing account's name. | Raises `DuplicateAccountNameError`. |
| Account Lifecycle | Failure Path | `test_reactivation_duplicate_name` | Reactivate an inactive account whose name conflicts with another account. | Raises `DuplicateAccountNameError`. |
| Monetary Conversion | Happy Path | `test_naira_to_kobo_conversion` | Input="250.50" | Returns integer `25050`. |
| Monetary Conversion | Edge Case | `test_minimum_valid_monetary_amount` | Input="0.01" | Returns integer `1`. |
| Monetary Conversion | Failure Path | `test_excessive_decimal_precision_rejected` | Input="250.555" | Raises `InvalidAmountError`. |
| Monetary Conversion | Failure Path | `test_zero_amount_rejected` | Input="0.00" | Raises `InvalidAmountError`. |
| Monetary Conversion | Failure Path | `test_non_numeric_amount_rejected` | Input="abc" | Raises `InvalidAmountError`. |
| Monetary Conversion | Failure Path | `test_transaction_ceiling_enforced` | Input="100000000.00" | Raises `InvalidAmountError`. |
| Date Validation | Happy Path | `test_today_date_is_accepted` | Transaction date: 2026-11-11; fixed today: 2026-11-11 | Date accepted successfully. |
| Date Validation | Happy Path | `test_past_date_is_accepted` | Transaction date: 2026-11-10; fixed today: 2026-11-11 | Date accepted successfully. |
| Date Validation | Failure Path | `test_future_date_is_rejected` | Transaction date: 2026-11-12; fixed today: 2026-11-11 | Raises `InvalidDateError`. |
| Date Validation | Failure Path | `test_invalid_calendar_date_is_rejected` | Transaction date: 2026-02-30 | Raises `InvalidDateError`. |
| Date Validation | Failure Path | `test_alternative_date_format_is_rejected` | Transaction date: 2026/11/11 | Raises `InvalidDateError`. |
| Balance Calculation | Happy Path | `test_ledger_derived_balance` | Income: 100,000 Kobo; expense: 25,000 Kobo | Returns 75,000 Kobo. |
| Balance Calculation | Invariant | `test_balance_matches_ledger_sum` | Multiple income, expense, transfer, and reversal records. | Calculated balance matches the cumulative ledger effect. |
| Balance Calculation | Invariant | `test_total_balance_matches_active_accounts` | Multiple active and inactive accounts. | Dashboard total equals the sum of active account balances only. |
| Transfer Processing | Happy Path | `test_transfer_preserves_combined_balance` | Source: 100,000 Kobo; transfer: 25,000 Kobo. | Source decreases by 25,000 Kobo and destination increases by 25,000 Kobo. |
| Transfer Processing | Invariant | `test_transfer_preserves_global_balance` | Multiple accounts and valid transfer. | Aggregate balance remains unchanged. |
| Account Lifecycle | Failure Path | `test_nonzero_balance_blocks_deactivation` | Ledger-derived balance: 1 Kobo. | Raises `AccountBalanceNotZeroError`. |
| Account Lifecycle | Happy Path | `test_zero_balance_allows_deactivation` | Ledger-derived balance: 0 Kobo. | Account status changes to INACTIVE. |
| Category Validation | Failure Path | `test_invalid_expense_category` | Category="Unconfigured Category". | Raises `InvalidCategoryError`. |
| Category Reporting | Invariant | `test_transfers_excluded_from_expense_breakdown` | Expense and transfer records. | Only effective expenses contribute to category totals. |
| Transaction Reversal | Happy Path | `test_reverse_income_transaction` | Existing income transaction. | Original target account is debited by the original amount. |
| Transaction Reversal | Happy Path | `test_reverse_expense_transaction` | Existing expense transaction. | Original source account receives the reversed amount. |
| Transaction Reversal | Happy Path | `test_reverse_transfer_transaction` | Existing transfer transaction. | Both original account movements are reversed correctly. |
| Transaction Reversal | Failure Path | `test_transaction_cannot_be_reversed_twice` | Already reversed transaction. | Raises `TransactionAlreadyReversedError`. |
| Transaction Reversal | Invariant | `test_original_transaction_remains_immutable` | Original transaction followed by reversal. | Original transaction attributes remain unchanged. |
| Transaction Reversal | Invariant | `test_reversal_restores_original_balance` | Valid original transaction and reversal. | Original account balances are restored, subject to subsequent transactions. |
| Transaction Capacity | Failure Path | `test_transaction_limit_blocks_new_entry` | Existing ledger contains 10,000 records. | Raises `TransactionCapacityExceededError`; no state mutation. |
| Transaction Capacity | Edge Case | `test_transaction_limit_allows_final_entry` | Existing ledger contains 9,999 records. | Transaction succeeds; ledger contains exactly 10,000 records. |

## 8.2 Integration Testing (Cross-Layer Subsystem Communication)

Integration tests must evaluate communication between the Business Logic Layer and Data Access Layer, specifically verifying that `wallet_engine.py` correctly updates and retrieves data through the storage implementation.

Unlike unit tests, these tests may use temporary physical storage files to verify actual JSON serialization and persistence behaviour.

| Targeted Interaction | Strategy | Test Function Identifier | Scenario Setup / Inputs | Expected Integration Outcome |
| --- | --- | --- | --- | --- |
| Atomic Entry Lifecycle | Happy Path | `test_business_action_triggers_file_flush` | Post a valid INCOME entry through `wallet_engine.py`. | Proposed state is persisted using atomic replacement before being committed to active memory. |
| Transaction Conflict | Failure Path | `test_balance_check_blocks_file_write` | Attempt an EXPENSE exceeding the account balance. | Raises `InsufficientFundsError`; no memory mutation or disk write occurs. |
| Persistence Failure | Failure Path | `test_failed_persistence_preserves_memory_state` | Attempt valid income while simulating a staging-file write failure. | `DatabaseWriteException` is raised; original memory and disk states remain unchanged. |
| Atomic Replacement Failure | Failure Path | `test_replace_failure_preserves_previous_file` | Simulate an `os.replace()` failure. | Proposed state is discarded; existing persisted file remains unchanged. |
| Transfer Atomicity | Happy Path | `test_transfer_updates_both_accounts_atomically` | Execute a valid transfer between two active accounts. | Both account balances and the transfer ledger record are persisted together. |
| Transfer Validation | Failure Path | `test_inactive_destination_blocks_transfer` | Attempt a transfer into an inactive account. | Raises `InactiveAccountError`; neither account nor ledger is modified. |
| Balance Reconciliation | Happy Path | `test_reconciliation_corrects_cached_balance` | Stored balance differs from ledger-derived balance. | Cached balance is corrected and persisted. |
| Reversal Persistence | Happy Path | `test_reversal_persists_original_and_reversal` | Reverse an existing transaction. | Original record remains unchanged and reversal record is persisted atomically. |
| Category Reporting | Happy Path | `test_expense_categories_loaded_correctly` | Retrieve expense category configuration. | Business Logic Layer uses the centrally defined category collection. |

## 8.3 Persistence and Restart Testing

The system must explicitly verify that committed application state survives a complete application reinitialization.

Restart testing must not simply reload data into the existing application object.

A fresh storage instance and Business Logic instance must be created to simulate a genuine application restart.

**Required scenarios:**

### Successful Restart Recovery

1. Initialize the application using a temporary JSON storage file.
2. Create an account.
3. Record an income transaction.
4. Close or discard the current application instance.
5. Create a new storage instance.
6. Create a new Business Logic instance using the new storage instance.
7. Load the persisted JSON state.
8. Verify that the account, transaction, and ledger-derived balance are correctly recovered.

**Expected outcome:**

The new application instance must reconstruct the same committed financial state as the previous instance.

### Failed Write Recovery

1. Initialize the application using a temporary JSON storage file.
2. Record a valid transaction.
3. Simulate a staging-file write failure during a subsequent transaction.
4. Verify that the previous JSON file remains unchanged.
5. Verify that the active in-memory state remains unchanged.
6. Create a fresh application instance.
7. Reload the JSON file.
8. Verify that only the previously committed transactions are present.

### Failed Atomic Replacement Recovery

1. Initialize the application with an existing valid JSON file.
2. Prepare a valid proposed state change.
3. Simulate an `os.replace()` failure.
4. Verify that the previous persisted file remains unchanged.
5. Verify that the proposed in-memory state is discarded.
6. Reload the file using a fresh application instance.
7. Verify that the previously committed state is recovered correctly.

## 8.4 End-to-End Testing (Terminal Simulation Workflow)

End-to-End testing must simulate a user interacting with the complete live CLI menu interface.

**Execution Framework:**

- Tests must use Python's `unittest.mock.patch` utility to inject sequential user inputs.
- Standard input (`sys.stdin`) must be simulated where appropriate.
- Terminal output (`sys.stdout`) must be captured and inspected.
- Tests must verify that complete user workflows produce the expected output and persisted state.

**Test Case Example:**

A complete end-to-end simulation must:

1. Boot the application and display the main menu.
2. Select the option to create a new account.
3. Supply a valid account name and account type.
4. Verify that the account is created with ACTIVE status and zero Kobo.
5. Select the income-recording option.
6. Supply a valid Naira amount, target account, transaction date, and descriptive label.
7. Verify that the monetary amount is converted into integer Kobo.
8. Verify that the account balance and transaction ledger are updated.
9. Navigate to the account balance view.
10. Verify that the displayed Naira balance matches the ledger-derived balance.
11. Navigate to transaction history and verify the recorded transaction.
12. Record an expense.
13. Verify that the expense appears under the correct category.
14. Execute a transfer between two active accounts.
15. Verify that the combined balance remains unchanged.
16. Reverse an incorrectly recorded transaction.
17. Verify that the original transaction remains visible and the reversal is recorded separately.
18. Navigate to the financial reporting interface.
19. Verify that reversed transactions do not distort effective income and expense totals.

The test must confirm that the complete user journey produces consistent results across the CLI, Business Logic Layer, and persisted JSON file.

## 8.5 Domain Invariant Testing

In addition to individual test cases, the application must test the following properties across relevant financial workflows.

### Invariant 1: Ledger Balance Consistency

For every account:

**Cached Account Balance = Ledger-Derived Account Balance**

The equality must hold after every successfully committed financial operation.

### Invariant 2: Aggregate Balance Consistency

**Total Active Account Balance = Sum of All Active Account Balances**

Inactive accounts must be excluded from the active dashboard total.

### Invariant 3: Transfer Conservation

For every valid transfer:

**Source Debit = Destination Credit**

The aggregate balance across all accounts must remain unchanged.

### Invariant 4: Reversal Conservation

For every successfully reversed transaction:

**Original Financial Effect + Reversal Financial Effect = Zero**

This must hold across all accounts affected by the original transaction.

### Invariant 5: Ledger Immutability

A successful reversal must never alter the original transaction's stored attributes.

### Invariant 6: Persistence Consistency

**Committed In-Memory State = Persisted JSON State**

Following every successful operation, the active application state must correspond to the newly persisted JSON state.

Following a failed persistence operation, the original in-memory and persisted states must remain unchanged.

### Invariant 7: Category Reporting Integrity

Only effective EXPENSE transactions may contribute to expense-category breakdowns.

TRANSFERS and REVERSALS must not be treated as ordinary expenses.

---
