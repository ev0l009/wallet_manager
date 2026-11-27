## **11.0 Explicit Out-of-Scope Decisions**

To ensure a reliable and focused implementation within the project timeline, the following technical capabilities are explicitly designated as out of scope.

The current release must not introduce code structures, abstractions, or implementation workflows solely to accommodate these excluded capabilities. They may only be considered if a future requirement formally changes the approved scope and architecture.

## **11.1 Identity and Session Security**

- **User Authentication and Authorization:** In alignment with ASM-01 (Single-User Execution Environment), the application will not feature user registration, password hashing, multi-user login gates, or session management.
- **Role-Based Access Control:** User roles, permission hierarchies, and access-control mechanisms are excluded from the current implementation.
- The application operates as a single-user local application without separate user identities or ownership boundaries.

## **11.2 Financial and Currency Scope Boundaries**

- **Multi-Currency Frameworks:** The system supports only one fiat currency: Nigerian Naira (₦).
- All monetary input, storage, calculations, and reporting operate in this single currency. Internal monetary values are represented as integer Kobo.
- Cross-border currency conversions, foreign exchange calculations, exchange-rate management, and multi-currency ledger balances are excluded.
- **Automated and Recurring Transactions:** The ledger handles manually recorded transactions only.
- Automated standing orders, recurring bill schedulers, scheduled transfers, and future salary automation are outside the current scope.

## **11.3 Infrastructure and Deployment Interfaces**

- **Web, Mobile, or Graphical Deployment:** The presentation layer is designed exclusively for a local Python Command-Line Interface.
- Web hosting architectures, RESTful API servers, mobile applications, desktop graphical interfaces, and browser-based interfaces are excluded.
- The application is intended to run locally on a supported environment using the documented Python runtime and setup instructions.

## **11.4 External Ecosystem Integrations**

- **External Open Banking APIs:** The application operates within a closed local data environment.
- It will not connect to live banking APIs, banking webhooks, external payment gateways such as Mono, Flutterwave, or Stripe, or real-time card authorization services.
- **Artificial Intelligence Modules:** Categorization and financial reporting rely on user input and conventional application logic.
- Predictive budgeting, AI-powered financial advisory systems, automated expense categorization, and machine-learning-based financial predictions are excluded.

## **11.5 Advanced Persistence and Concurrency**

- **Database Management Systems:** SQLite, PostgreSQL, and other database management systems are excluded from the current implementation. JSON flat-file persistence is the exclusive storage mechanism.
- **Interchangeable Storage Backends:** The architecture will use the concrete JSON Data Access Layer directly. Abstract storage interfaces and backend-switching mechanisms are excluded.
- **Multi-Process Concurrency:** Concurrent writers, multi-process file synchronization, and concurrent application instances modifying the same storage file are outside the supported execution model.
- **Advanced Disaster Recovery:** Automated backup scheduling, point-in-time recovery, distributed replication, and automated restoration workflows are excluded.
- The current architecture relies on the documented JSON persistence mechanism, including temporary-file staging and atomic replacement through `os.replace()`.
- Atomic replacement does not constitute a backup or disaster-recovery mechanism and does not guarantee protection against every hardware, filesystem, or operating-system failure.

These exclusions define the boundaries of the current release. They do not prevent future scope changes, but any such changes must be formally reviewed against the existing requirements, business rules, and architecture before implementation.

---