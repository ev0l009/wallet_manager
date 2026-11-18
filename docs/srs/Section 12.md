# 12.0 Document-Wide Technical Consistency Rules

The following rules consolidate the most important implementation constraints and must be treated as mandatory throughout development.

1. **Monetary storage:** Every monetary amount must be stored as an integer Kobo value.
2. **Monetary input:** User-entered Naira amounts must be parsed using `Decimal`, validated, multiplied by 100, and converted to integer Kobo.
3. **No floating-point calculations:** Python `float` must never be used for monetary calculations, balance storage, or financial aggregation.
4. **Ledger authority:** The transaction ledger is the authoritative source for account balances.
5. **Cached balances:** `acc_bal` is a cached integer Kobo representation and must be reconciled against the ledger.
6. **Transaction integrity:** Every financial operation must update the relevant account balances and transaction ledger as one logical operation.
7. **Persistence integrity:** Proposed application state must be persisted through the staging-file and atomic replacement strategy before being committed to active memory.
8. **Transfer classification:** Transfers must remain separate from standalone income and expense reporting totals.
9. **Account lifecycle:** Inactive accounts must not participate in new financial transactions.
10. **Deactivation validation:** An account can only be deactivated when its ledger-derived balance is exactly zero Kobo.
11. **Account uniqueness:** Account names must be unique across both active and inactive accounts, using case-insensitive comparison.
12. **Account identification:** Account IDs must be generated internally and must remain stable throughout the account's lifetime.
13. **Initial account balance:** Every new account must begin with zero Kobo. Initial funding must be recorded through a valid INCOME transaction.
14. **Date integrity:** Transaction dates must follow the exact YYYY-MM-DD format and must not be future-dated.
15. **Expense categories:** Permitted expense categories must be centrally defined and validated through the Business Logic Layer.
16. **Transaction immutability:** Historical transaction records must never be directly edited or deleted.
17. **Transaction correction:** Incorrect financial transactions must be corrected through compensating REVERSAL transactions.
18. **Reversal integrity:** A transaction may be reversed only once, and every reversal must reference its original transaction.
19. **Reporting integrity:** Reversed original transactions and their corresponding reversals must not distort ordinary income and expense totals.
20. **Transaction capacity:** The JSON ledger must enforce the maximum supported capacity of 10,000 historical transaction records.
21. **Layer separation:** The Presentation Layer must not perform financial calculations or access persistence files directly.
22. **Dependency direction:** The UI depends on the Business Logic Layer, while the Business Logic Layer depends on an abstract storage contract implemented by the Data Access Layer.
23. **Storage isolation:** The Data Access Layer must not import or depend on Business Logic or Presentation modules.
24. **Error handling:** Expected validation, business-rule, and persistence failures must be represented through the common `WalletError` exception hierarchy.
25. **UI error handling:** The Presentation Layer must catch expected application exceptions at appropriate user-operation boundaries.
26. **Unexpected failures:** The top-level application boundary must log unexpected exceptions and terminate safely.
27. **Testing isolation:** Business Logic unit tests must use injected in-memory storage implementations rather than physical disk operations.
28. **Persistence testing:** Integration tests must verify successful persistence, staging-file failures, atomic replacement failures, and recovery after a fresh application restart.
29. **Mathematical integrity:** Account balances must reconcile with the cumulative financial effects of the complete transaction ledger, including reversals.
30. **Typing:** Public functions, domain entities, and cross-layer interfaces must use consistent Python type annotations.
31. **Documentation:** Implementation documentation must remain aligned with the requirements, business rules, and actual application behaviour.

These rules take precedence over illustrative examples wherever an example might otherwise appear inconsistent with the formal business requirements.

---

**END OF DOCUMENT**