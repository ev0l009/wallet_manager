# 11.0 Explicit Out-of-Scope Decisions

To ensure a reliable and focused implementation within the project timeline, the following technical capabilities are explicitly designated as out of scope.

No code structures or implementation workflows will be engineered to support these features in the current release unless a future requirement formally introduces them.

## 11.1 Identity and Session Security

- **User Authentication and Authorization:** In alignment with ASM-01 (Single-User Execution Environment), the application will not feature registration screens, password hashing, multi-user login gates, or session management.
- **Role-Based Access Control:** Permission hierarchies and user roles are excluded from the current implementation.

## 11.2 Financial and Currency Scope Boundaries

- **Multi-Currency Frameworks:** The system is built exclusively around a single fiat currency: Nigerian Naira (₦).
- Cross-border currency conversions, foreign exchange calculations, and multi-currency ledger balances are excluded.
- **Automated and Recurring Transactions:** The ledger will handle manually recorded transactions only.
- Automated standing orders, recurring bill schedulers, and future salary automation are outside the current scope.

## 11.3 Infrastructure and Deployment Interfaces

- **Web, Mobile, or Graphical Deployment:** The presentation layer is designed exclusively for a localized Python Command-Line Interface.
- Web hosting architectures, RESTful API servers, mobile applications, and graphical user interfaces are excluded.

## 11.4 External Ecosystem Integrations

- **External Open Banking APIs:** The engine operates within a closed local data environment.
- The application will not connect to live banking webhooks, external payment gateways such as Mono, Flutterwave, or Stripe, or real-time card authorization APIs.
- **Artificial Intelligence Modules:** Categorization and financial reports will rely entirely on user input and conventional application logic.
- Predictive budgeting, AI-powered financial advisory systems, and automated expense categorization are excluded.

## 11.5 Advanced Persistence and Concurrency

- **Database Management Systems:** SQLite, PostgreSQL, and other database management systems are excluded from the current implementation.
- **Multi-Process Concurrency:** Concurrent writers and multi-process file synchronization are outside the supported execution model.
- **Advanced Disaster Recovery:** Automated backup scheduling, point-in-time recovery, and distributed replication are excluded.
- The current architecture relies on the documented JSON persistence and atomic replacement strategy.

---
