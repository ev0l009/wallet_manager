## **10.0 Documentation Approach**

The application must maintain a lightweight but consistent documentation structure covering installation, usage, architecture, and implementation decisions.

## **10.1 README Documentation**

The root `README.md` must provide:

- Project overview and objectives.
- Core application features.
- Python version requirements.
- Installation and setup instructions.
- Application execution instructions.
- CLI usage guidance.
- Supported account types and transaction classifications.
- Supported income and expense categories.
- Important monetary and transaction constraints, including the use of integer Kobo internally and the maximum transaction amount.
- Testing instructions.
- Known limitations and out-of-scope capabilities.

The README must serve as the primary entry point for developers and users. Instructions and examples must reflect the application's actual behaviour.

## **10.2 Inline Documentation and Docstrings**

- Each major module must include a module-level docstring explaining its responsibility.
- Public classes and methods must include docstrings describing their purpose.
- Functions with non-obvious parameters or return values must document their expected inputs and outputs.
- Functions that raise application-specific exceptions must document the relevant exceptions where this information is not otherwise clear from their contracts.
- Complex financial calculations must include concise explanations of their mathematical behaviour.
- Comments should explain non-obvious implementation decisions rather than repeat the code.
- Documentation must distinguish between monetary input parsing using `Decimal` and internal monetary calculations using integer Kobo.
- Docstrings must describe actual implementation behaviour and must not introduce unsupported capabilities or architectural abstractions.

## **10.3 Architecture Documentation**

The `docs/architecture.md` file must document:

- The three-tier architecture and the responsibilities of the Presentation, Business Logic, and Data Access layers.
- Dependency direction, including the direct dependency of the Business Logic layer on the concrete JSON Data Access Layer.
- Domain entity responsibilities and validation boundaries.
- The concrete JSON persistence implementation and its responsibilities.
- The atomic file replacement strategy and its limitations.
- Ledger-derived balance calculations, including the treatment of inactive accounts.
- Transaction immutability and correction through ordinary compensating transactions.
- The application exception hierarchy and error-handling responsibilities.
- Testing boundaries and expected coverage across the application layers.

Architecture documentation must not describe an abstract storage interface, interchangeable persistence backends, cached account balances, or a separate transaction reversal mechanism as part of the current design.

## **10.4 Business Rule Traceability**

- Important implementation decisions should reference their corresponding requirement or business rule identifiers where practical.
- Changes to business rules must be reflected in the relevant implementation documentation.
- Documentation must remain consistent with the current application behaviour and approved architectural decisions.
- Outdated examples, descriptions, and code references must be updated when their underlying requirements or implementation change.
- Where a documented implementation decision differs from an earlier design assumption, the documentation must reflect the currently approved decision.

## **10.5 Documentation Maintenance**

Documentation must be maintained alongside implementation changes.

A feature must not be considered fully documented if its relevant requirements, business rules, architecture descriptions, or usage instructions have become inconsistent with its actual behaviour.

Documentation updates must accompany changes that affect:

- User-facing functionality or CLI workflows.
- Business rules and validation behaviour.
- Domain entities and transaction handling.
- Persistence behaviour and data integrity.
- Application exceptions and error handling.
- Testing procedures or project setup instructions.

The documentation must describe the current implementation rather than proposed, deprecated, or hypothetical functionality.

---