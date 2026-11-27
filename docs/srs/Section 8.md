# **8.0 Testing Strategy**

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

Tests must verify the behavior of the established three-tier architecture, including the direct dependency of the Business Logic Layer on the concrete JSON Data Access Layer.

## **8.1 Unit Testing (Isolated Functional Integrity)**

Unit tests must isolate specific business functions, domain validation mechanisms, and calculation logic.

External dependencies, particularly physical disk operations and date providers, must be controlled through temporary files, mocks, or other suitable test doubles.

The Business Logic Layer must depend directly on the concrete JSON Data Access Layer. An abstract storage interface or interchangeable in-memory storage implementation must not be introduced for testing purposes.

Unit tests must not require access to the application's actual production JSON storage file.

**Example unit test coverage:**

| Targeted Module        | Strategy     | Test Function Identifier                                      | Test Parameters / Inputs                                                                                          | Expected Outcome                                                                                                       |
| ---------------------- | ------------ | ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Account Creation       | Happy Path   | `test_create_account_success`                                 | name="Polaris Bank", type="BANK"                                                                                  | Account receives an automatically generated ID, ACTIVE status, and a ledger-derived balance of zero Kobo.              |
| Account Creation       | Failure Path | `test_create_account_name_too_short`                          | name="Pol", type="BANK"                                                                                           | Raises `InvalidAccountNameError`.                                                                                      |
| Account Creation       | Edge Case    | `test_create_account_exact_lower_bound`                       | name="Opay", type="MOBILE_WALLET"                                                                                 | Account initialized successfully.                                                                                      |
| Account Creation       | Failure Path | `test_duplicate_account_name_case_insensitive`                | Existing name="Cash"; new name="cash"                                                                             | Raises `DuplicateAccountNameError`.                                                                                    |
| Account Creation       | Failure Path | `test_duplicate_name_inactive_account`                        | Existing inactive account name="Cash"; new name="Cash"                                                            | Raises `DuplicateAccountNameError`.                                                                                    |
| Account Creation       | Happy Path   | `test_account_id_generated_by_service`                        | Valid account creation.                                                                                           | ID is generated internally by the Business Logic Layer.                                                                |
| Account Creation       | Invariant    | `test_new_account_has_zero_ledger_balance`                    | Valid account creation without transactions.                                                                      | Calculated account balance equals zero Kobo.                                                                           |
| Account Lifecycle      | Happy Path   | `test_rename_account_success`                                 | Rename existing account to an unused valid name.                                                                  | Name updated without changing account ID or historical references.                                                     |
| Account Lifecycle      | Failure Path | `test_rename_account_duplicate_name`                          | Rename account to another existing account's name.                                                                | Raises `DuplicateAccountNameError`.                                                                                    |
| Account Lifecycle      | Failure Path | `test_reactivation_duplicate_name`                            | Reactivate an inactive account whose name conflicts with another account.                                         | Raises `DuplicateAccountNameError`.                                                                                    |
| Account Lifecycle      | Happy Path   | `test_inactive_account_balance_can_be_inspected`              | Inspect an inactive account with historical transactions.                                                         | Correct ledger-derived balance is returned.                                                                            |
| Monetary Conversion    | Happy Path   | `test_naira_to_kobo_conversion`                               | Input="250.50"                                                                                                    | Returns integer `25050`.                                                                                               |
| Monetary Conversion    | Edge Case    | `test_minimum_valid_monetary_amount`                          | Input="0.01"                                                                                                      | Returns integer `1`.                                                                                                   |
| Monetary Conversion    | Failure Path | `test_excessive_decimal_precision_rejected`                   | Input="250.555"                                                                                                   | Raises `InvalidAmountError`.                                                                                           |
| Monetary Conversion    | Failure Path | `test_zero_amount_rejected`                                   | Input="0.00"                                                                                                      | Raises `InvalidAmountError`.                                                                                           |
| Monetary Conversion    | Failure Path | `test_non_numeric_amount_rejected`                            | Input="abc"                                                                                                       | Raises `InvalidAmountError`.                                                                                           |
| Monetary Conversion    | Failure Path | `test_transaction_ceiling_enforced`                           | Input="100000000.00"                                                                                              | Raises `InvalidAmountError`.                                                                                           |
| Monetary Conversion    | Edge Case    | `test_transaction_ceiling_accepted`                           | Input="99999999.99"                                                                                               | Returns integer `9999999999`.                                                                                          |
| Date Validation        | Happy Path   | `test_today_date_is_accepted`                                 | Transaction date equals the injected current date.                                                                | Date accepted successfully.                                                                                            |
| Date Validation        | Happy Path   | `test_past_date_is_accepted`                                  | Transaction date precedes the injected current date.                                                              | Date accepted successfully.                                                                                            |
| Date Validation        | Failure Path | `test_future_date_is_rejected`                                | Transaction date follows the injected current date.                                                               | Raises `InvalidDateError`.                                                                                             |
| Date Validation        | Failure Path | `test_invalid_calendar_date_is_rejected`                      | Transaction date="2026-02-30"                                                                                     | Raises `InvalidDateError`.                                                                                             |
| Date Validation        | Failure Path | `test_alternative_date_format_is_rejected`                    | Transaction date="2026/11/11"                                                                                     | Raises `InvalidDateError`.                                                                                             |
| Balance Calculation    | Happy Path   | `test_ledger_derived_balance`                                 | Income: 100,000 Kobo; expense: 25,000 Kobo.                                                                       | Returns 75,000 Kobo.                                                                                                   |
| Balance Calculation    | Invariant    | `test_balance_matches_ledger_sum`                             | Multiple income, expense, and transfer records.                                                                   | Calculated balance matches the cumulative ledger effect.                                                               |
| Balance Calculation    | Invariant    | `test_active_total_excludes_inactive_accounts`                | Multiple active and inactive accounts with ledger histories.                                                      | Active total equals the sum of active account balances only.                                                           |
| Balance Calculation    | Invariant    | `test_inactive_account_balance_is_not_in_active_total`        | Inactive account with a non-zero ledger-derived balance.                                                          | Individual balance remains inspectable but is excluded from active totals and net worth.                               |
| Balance Calculation    | Invariant    | `test_backdated_transaction_recalculates_subsequent_balances` | Insert a backdated transaction affecting an account with later transactions.                                      | Complete chronological validation detects any resulting negative balance.                                              |
| Balance Calculation    | Edge Case    | `test_same_date_transactions_use_insertion_order`             | Multiple transactions sharing the same financial date.                                                            | Running balances follow persisted insertion order.                                                                     |
| Balance Calculation    | Happy Path   | `test_backdated_transaction_predates_account_creation`        | Account exists in loaded collection but was created after the transaction's financial date.                       | Transaction is accepted if all other validation rules pass.                                                            |
| Transfer Processing    | Happy Path   | `test_transfer_preserves_combined_balance`                    | Source: 100,000 Kobo; transfer: 25,000 Kobo.                                                                      | Source decreases by 25,000 Kobo and destination increases by 25,000 Kobo.                                              |
| Transfer Processing    | Invariant    | `test_transfer_preserves_global_balance`                      | Multiple accounts and a valid transfer.                                                                           | Aggregate balance across all accounts remains unchanged.                                                               |
| Account Lifecycle      | Failure Path | `test_nonzero_balance_blocks_deactivation`                    | Ledger-derived balance: 1 Kobo.                                                                                   | Raises `AccountBalanceNotZeroError`.                                                                                   |
| Account Lifecycle      | Happy Path   | `test_zero_balance_allows_deactivation`                       | Ledger-derived balance: 0 Kobo.                                                                                   | Account status changes to INACTIVE.                                                                                    |
| Category Validation    | Failure Path | `test_invalid_expense_category`                               | Category="Unconfigured Category".                                                                                 | Raises `InvalidCategoryError`.                                                                                         |
| Category Reporting     | Invariant    | `test_transfers_excluded_from_expense_breakdown`              | Expense and transfer records.                                                                                     | Only EXPENSE transactions contribute to category totals.                                                               |
| Transaction Correction | Happy Path   | `test_counteract_income_with_expense`                         | Existing income transaction and an equal compensating expense.                                                    | Compensating expense produces the opposite financial effect.                                                           |
| Transaction Correction | Happy Path   | `test_counteract_expense_with_income`                         | Existing expense transaction and an equal compensating income.                                                    | Compensating income produces the opposite financial effect.                                                            |
| Transaction Correction | Happy Path   | `test_counteract_transfer_with_opposite_transfer`             | Existing transfer and an equal transfer with swapped account references.                                          | Original account movements are counteracted correctly.                                                                 |
| Transaction Correction | Invariant    | `test_compensating_transaction_preserves_original`            | Original transaction followed by a compensating transaction.                                                      | Original transaction attributes remain unchanged.                                                                      |
| Transaction Correction | Invariant    | `test_complete_compensation_restores_original_balance`        | Original transaction and equal compensating transaction, with no intervening transactions affecting the accounts. | Original ledger-derived balances are restored.                                                                         |
| Transaction Capacity   | Failure Path | `test_transaction_limit_blocks_new_entry`                     | Existing ledger contains 10,000 records.                                                                          | Raises `TransactionCapacityExceededError`; no state mutation.                                                          |
| Transaction Capacity   | Edge Case    | `test_transaction_limit_allows_final_entry`                   | Existing ledger contains 9,999 records.                                                                           | Transaction succeeds; ledger contains exactly 10,000 records.                                                          |
| Transaction Capacity   | Invariant    | `test_account_lifecycle_allowed_at_capacity`                  | Existing ledger contains 10,000 records.                                                                          | Account creation, renaming, deactivation, and reactivation remain available when their own business rules permit them. |

## **8.2 Integration Testing (Cross-Layer Subsystem Communication)**

Integration tests must evaluate communication between the Business Logic Layer and the concrete JSON Data Access Layer.

These tests must verify that business operations correctly construct proposed application states, invoke JSON persistence, and commit active in-memory state only after successful file replacement.

Unlike isolated unit tests, integration tests may use temporary physical JSON storage files to verify actual serialization, filesystem operations, and persistence behaviour.

| Targeted Interaction        | Strategy     | Test Function Identifier                                     | Scenario Setup / Inputs                                                                      | Expected Integration Outcome                                                                                    |
| --------------------------- | ------------ | ------------------------------------------------------------ | -------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| State Persistence           | Happy Path   | `test_business_action_persists_proposed_state`               | Post a valid INCOME transaction through the Business Logic Layer.                            | Proposed state is serialized and persisted using atomic replacement before becoming active in memory.           |
| Transaction Conflict        | Failure Path | `test_balance_check_blocks_file_write`                       | Attempt an EXPENSE exceeding the account balance.                                            | Raises `InsufficientFundsError`; no memory mutation or persistence operation occurs.                            |
| Persistence Failure         | Failure Path | `test_failed_persistence_preserves_memory_state`             | Attempt valid income while simulating a staging-file write failure.                          | `StorageWriteError` is raised; original memory and disk states remain unchanged.                                |
| Atomic Replacement Failure  | Failure Path | `test_replace_failure_preserves_previous_file`               | Simulate an `os.replace()` failure.                                                          | Proposed state is discarded; existing persisted file remains unchanged.                                         |
| Transfer Atomicity          | Happy Path   | `test_transfer_updates_both_accounts_atomically`             | Execute a valid transfer between two active accounts.                                        | Both account effects and the single TRANSFER ledger record are persisted together.                              |
| Transfer Validation         | Failure Path | `test_inactive_destination_blocks_transfer`                  | Attempt a transfer into an inactive account.                                                 | Raises `InactiveAccountError`; neither account nor ledger is modified.                                          |
| Balance Reconciliation      | Invariant    | `test_ledger_balance_remains_authoritative`                  | Load accounts and transactions from JSON containing no account balance fields.               | Account balances are calculated from transaction history without reading or creating cached balance attributes. |
| Correction Persistence      | Happy Path   | `test_compensating_transaction_persists_atomically`          | Record a valid compensating transaction.                                                     | Original transaction remains unchanged and the new ordinary transaction is persisted atomically.                |
| Category Reporting          | Happy Path   | `test_expense_categories_loaded_correctly`                   | Retrieve expense category configuration.                                                     | Business Logic Layer uses the centrally defined category collection.                                            |
| Inactive Account Inspection | Happy Path   | `test_inactive_account_history_loads_correctly`              | Load an inactive account with historical transactions.                                       | Account history and ledger-derived balance remain accessible.                                                   |
| Chronological Integrity     | Failure Path | `test_backdated_transaction_that_breaks_history_is_rejected` | Attempt a backdated transaction that causes a subsequent running balance to become negative. | Raises the appropriate balance validation exception; no persistence or memory mutation occurs.                  |

## **8.3 Persistence and Restart Testing**

The system must explicitly verify that committed application state survives a complete application reinitialization.

Restart testing must not simply reload data into the existing application object.

A fresh Data Access Layer instance and Business Logic Layer instance must be created to simulate a genuine application restart.

**Required scenarios:**

### **Successful Restart Recovery**

1. Initialize the application using a temporary JSON storage file.
2. Create an account.
3. Record an income transaction.
4. Record an expense transaction.
5. Close or discard the current application instance.
6. Create a new Data Access Layer instance using the same storage file.
7. Create a new Business Logic Layer instance using the new Data Access Layer instance.
8. Load the persisted JSON state.
9. Verify that the account, transactions, and ledger-derived balance are correctly recovered.
10. Verify that account status and transaction history are preserved.

**Expected outcome:**

The new application instance must reconstruct the same committed financial state as the previous instance.

### **Failed Write Recovery**

1. Initialize the application using a temporary JSON storage file.
2. Record a valid transaction.
3. Simulate a staging-file write failure during a subsequent transaction.
4. Verify that the previous JSON file remains unchanged.
5. Verify that the active in-memory state remains unchanged.
6. Create a fresh application instance.
7. Reload the JSON file.
8. Verify that only the previously committed transactions are present.

### **Failed Atomic Replacement Recovery**

1. Initialize the application with an existing valid JSON file.
2. Prepare a valid proposed state change.
3. Simulate an `os.replace()` failure.
4. Verify that the previous persisted file remains unchanged.
5. Verify that the proposed in-memory state is discarded.
6. Reload the file using a fresh application instance.
7. Verify that the previously committed state is recovered correctly.

### **Invalid Persisted Data Recovery**

1. Initialize the application with a valid JSON storage file.
2. Modify a copy of the file to introduce a persisted-data integrity violation.
3. Create a fresh application instance.
4. Attempt to load the modified file.
5. Verify that the appropriate integrity exception prevents startup.
6. Verify that the invalid file is not silently replaced with an empty application state.

Test cases must include malformed JSON, invalid entity fields, duplicate identifiers, invalid transaction references, and historical negative balances.

### **Missing Storage Initialization**

1. Initialize the application using a temporary directory without a `storage.json` file.
2. Create a fresh Data Access Layer instance.
3. Invoke `load_app_data()`.
4. Verify that an empty `WalletEngineData` state is returned.
5. Verify that the application can subsequently persist its first successful state change.

**Expected outcome:**

A missing storage file must be treated as a first-run condition, not as a persistence integrity failure.

## **8.4 End-to-End Testing (Terminal Simulation Workflow)**

End-to-End testing must simulate a user interacting with the complete live CLI menu interface.

**Execution Framework:**

- Tests must use Python's `unittest.mock.patch` utility to inject sequential user inputs.
- Standard input (`sys.stdin`) must be simulated where appropriate.
- Terminal output (`sys.stdout`) must be captured and inspected.
- Tests must verify that complete user workflows produce the expected output and persisted state.
- Tests must use isolated temporary storage files rather than the production storage file.

**Test Case Example:**

A complete end-to-end simulation must:

1. Boot the application and display the main menu.
2. Select the option to create a new account.
3. Supply a valid account name and account type.
4. Verify that the account is created with ACTIVE status and a ledger-derived balance of zero Kobo.
5. Select the income-recording option.
6. Supply a valid Naira amount, target account, transaction date, and descriptive label.
7. Verify that the monetary amount is converted into integer Kobo.
8. Verify that the account's ledger-derived balance reflects the recorded income.
9. Navigate to the account balance view.
10. Verify that the displayed Naira balance matches the ledger-derived balance.
11. Navigate to transaction history and verify the recorded transaction.
12. Record an expense.
13. Verify that the expense appears under the correct category.
14. Execute a transfer between two active accounts.
15. Verify that the combined balance remains unchanged.
16. Record an ordinary compensating transaction for an incorrectly recorded transaction.
17. Verify that the original transaction remains unchanged and visible in transaction history.
18. Verify that the compensating transaction appears as a separate ordinary transaction.
19. Navigate to the financial reporting interface.
20. Verify that income, expenses, and transfers are included or excluded according to their ordinary transaction classifications.
21. Verify that the account balances and financial reports remain consistent with the persisted JSON ledger.

The test must confirm that the complete user journey produces consistent results across the CLI, Business Logic Layer, and persisted JSON file.

## **8.5 Domain Invariant Testing**

In addition to individual test cases, the application must test the following properties across relevant financial workflows.

### **Invariant 1: Ledger Balance Consistency**

**Account Balance = Ledger-Derived Account Balance**

Every account balance must be calculated exclusively from its associated transaction records.

No independently stored or cached account balance may exist.

### **Invariant 2: Aggregate Balance Consistency**

**Total Active Account Balance = Sum of All Active Account Balances**

Inactive accounts must be excluded from the active dashboard total and aggregate net worth.

Their individual ledger-derived balances must remain available for inspection when explicitly requested.

### **Invariant 3: Transfer Conservation**

For every valid transfer:

**Source Debit = Destination Credit**

The aggregate balance across all accounts must remain unchanged.

### **Invariant 4: Compensating Transaction Conservation**

For a complete compensation of an original transaction:

**Original Financial Effect + Compensating Financial Effect = Zero**

This must hold across all accounts affected by the original transaction.

The compensating transaction must use an ordinary transaction classification and must not modify the original transaction.

### **Invariant 5: Ledger Immutability**

Recording a compensating transaction must never alter the original transaction's stored attributes.

Original and compensating transactions must remain independently identifiable and visible in transaction history.

### **Invariant 6: Persistence Consistency**

**Committed In-Memory State = Persisted JSON State**

Following every successful operation, the active application state must correspond to the newly persisted JSON state.

Following a failed persistence operation, the original in-memory and persisted states must remain unchanged.

### **Invariant 7: Category Reporting Integrity**

Only EXPENSE transactions may contribute to expense-category breakdowns.

INCOME and TRANSFER transactions must not be treated as ordinary expenses.

Compensating transactions must contribute according to their ordinary classifications.

### **Invariant 8: Chronological Balance Integrity**

For every account, the running balance must never become negative at any point in chronological transaction order.

Transactions must be evaluated by:

1. Financial date in ascending order.
2. Persisted insertion order for transactions sharing the same financial date.

Backdated transactions must trigger revalidation of all affected subsequent transactions.

Account creation timestamps must not invalidate otherwise valid backdated transactions when the referenced account exists in the loaded account collection at transaction entry.

### **Invariant 9: Account Lifecycle Integrity**

Only ACTIVE accounts may participate in new INCOME, EXPENSE, or TRANSFER operations.

INACTIVE accounts must retain their historical transaction associations and ledger-derived balances.

Deactivation must not delete, modify, or otherwise alter historical transactions.

### **Invariant 10: Monetary Precision**

All persisted monetary values and financial calculations must use integer Kobo.

No transaction or account balance calculation may rely on binary floating-point arithmetic.

### **Invariant 11: Transaction Capacity Integrity**

The transaction ledger must never exceed 10,000 historical records.

A rejected transaction that would exceed the maximum must leave the active in-memory state and persisted JSON file unchanged.

Account lifecycle operations must remain available because they do not increase the transaction count.

---