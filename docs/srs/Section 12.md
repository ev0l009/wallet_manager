# **12.0 Document-Wide Technical Consistency Rules**

The following rules consolidate the most important implementation constraints and must be treated as mandatory throughout development.

These rules take precedence over illustrative examples, informal descriptions, and earlier assumptions wherever inconsistencies arise. They must remain aligned with the approved requirements, business rules, architecture, and implementation.

1\. **Monetary storage:** Every monetary amount must be represented internally and persisted as an integer Kobo value.

2\. **Monetary input:** User-entered Naira amounts must be parsed using Python's `Decimal`, validated, multiplied by 100, and converted to integer Kobo.

3\. **No floating-point calculations:** Python `float` must never be used for monetary calculations, balance calculations, financial aggregation, or monetary persistence.

4\. **Ledger authority:** The complete transaction ledger is the sole authoritative source for account balances.

5\. **No cached balances:** Account entities must not contain `acc_bal`, balance attributes, or other cached monetary representations. Balances must be calculated from transaction history whenever required.

6\. **Financial operation integrity:** Every financial operation must construct and validate the proposed transaction and resulting application state as one logical operation. Account balances must be derived from the resulting ledger rather than separately maintained.

7\. **Persistence integrity:** Proposed application state must be validated and persisted through the staging-file and atomic replacement strategy before it is committed to active in-memory state.

8\. **Transfer classification:** Transfers must remain separate from standalone income and expense reporting totals. They must, however, be reflected in the relevant account balances and account activity records.

9\. **Account lifecycle:** Inactive accounts must not participate in new income, expense, or transfer transactions. Their historical transactions and ledger-derived balances must remain available for inspection.

10\. **Deactivation validation:** An account can only be deactivated when its ledger-derived balance is exactly zero Kobo.

11\. **Account uniqueness:** Account names must be unique across both active and inactive accounts, using trimmed, case-insensitive comparison.

12\. **Account identification:** Account IDs must be generated internally by the Business Logic Layer and must remain stable throughout the account's lifetime.

13\. **Initial account balance:** Every new account must begin with a ledger-derived balance of zero Kobo. Initial funding must be recorded through a valid `INCOME` transaction.

14\. **Date integrity:** Transaction dates must follow the exact `YYYY-MM-DD` format and must not be future-dated. Backdated transactions may reference accounts created after the transaction's financial date, provided those accounts exist in the application's loaded account collection when the transaction is entered.

15\. **Category validation:** Permitted income and expense categories must be centrally defined and validated through the Business Logic Layer. Transfers must have a null category.

16\. **Transaction immutability:** Historical transaction records must never be directly edited or deleted.

17\. **Transaction correction:** Incorrect financial transactions must be corrected through ordinary compensating transactions using the existing `INCOME`, `EXPENSE`, or `TRANSFER` classifications. A dedicated `REVERSAL` transaction type, reversal relationship, or reversal-specific business logic must not be introduced.

18\. **Compensating transaction integrity:** Compensating transactions must produce the intended financial effect, comply with ordinary validation and chronological balance rules, and be persisted as separate transaction records. Transfer corrections must use an opposite transfer with the original source and destination accounts swapped.

19\. **Reporting integrity:** Original transactions and their compensating transactions must remain visible and be included in reports according to their ordinary transaction classifications. Transfers must remain excluded from standalone income and expense totals. No reversal-specific reporting exclusions must be implemented.

20\. **Transaction capacity:** The JSON ledger must enforce an absolute maximum capacity of 10,000 historical transaction records. A warning threshold must be applied at 4,000 records, with approximately 5,000 records representing the intended operational workload. Reaching the transaction limit must prevent additional transactions but must not prevent account lifecycle operations.

21\. **Layer separation:** The Presentation Layer must not perform financial calculations, enforce business rules independently, or access persistence files directly. These responsibilities belong to the Business Logic and Data Access Layers respectively.

22\. **Dependency direction:** The Presentation Layer depends on the Business Logic Layer. The Business Logic Layer depends directly on the concrete JSON Data Access Layer. No abstract storage contract or interchangeable persistence backend must be introduced.

23\. **Storage isolation:** The Data Access Layer must not import or depend on Business Logic or Presentation modules. It is responsible for persistence operations and storage-level validation, not application workflows or user interaction.

24\. **Error handling:** Expected validation, business-rule, entity lookup, data-integrity, and persistence failures must be represented through the common `WalletError` exception hierarchy.

25\. **UI error handling:** The Presentation Layer must catch expected application exceptions at appropriate user-operation boundaries and present understandable error messages without exposing internal implementation details.

26\. **Unexpected failures:** The top-level application boundary must log unexpected exceptions and terminate safely without presenting an unsuccessful operation as successful.

27\. **Testing isolation:** Business Logic unit tests must isolate external dependencies using mocks, controlled fixtures, or other suitable test doubles. They must not require physical persistence operations for ordinary unit testing. The production architecture must not introduce an abstract storage interface or interchangeable in-memory backend solely to facilitate testing.

28\. **Persistence testing:** Integration tests must use the concrete JSON Data Access Layer with temporary storage files. They must verify successful persistence, staging-file failures, atomic replacement failures, preservation of existing state after failed writes, and consistency after a fresh application restart.

29\. **Mathematical integrity:** Every account balance must reconcile with the cumulative financial effects of its complete transaction history, including ordinary compensating transactions. No separately stored balance may override the result derived from the ledger.

30\. **Typing:** Public functions, domain entities, and cross-layer method contracts must use consistent Python type annotations. Dynamic JSON data must be validated before being treated as typed application data.

31\. **Documentation:** Implementation documentation must remain aligned with the requirements, business rules, approved architecture, and actual application behaviour.

**END OF DOCUMENT**