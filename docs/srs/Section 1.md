# 1\. Introduction

## 1.1 Purpose

This Software Requirements Specification (SRS) document defines the functional requirements, non-functional requirements, architectural constraints, business rules, and technical expectations governing the development of the Wallet Manager application.

The document establishes a formal reference for the application's expected behaviour, internal structure, data management mechanisms, and implementation boundaries.

Its primary purpose is to provide a clear and consistent technical specification that guides implementation while minimizing ambiguity and preventing inconsistencies across application components.

The specification also serves as a reference for development decisions, validation activities, automated testing, and future maintenance.

## 1.2 Project Scope

Wallet Manager is a localized, single-user financial management application designed to provide basic personal financial tracking through an interactive Python Command-Line Interface (CLI).

The application enables users to create and manage financial accounts, record completed financial transactions, monitor account balances, retrieve transaction histories, and generate financial summaries.

The system uses a transaction-ledger approach in which historical financial records serve as the authoritative source for account balance calculations.

Its core capabilities include:

- **Account Management:** Creating, renaming, deactivating, and reactivating financial accounts while enforcing account identity and lifecycle constraints.
- **Transaction Management:** Recording INCOME, EXPENSE, and TRANSFER transactions against valid financial accounts.
- **Transaction Correction:** Correcting incorrectly recorded transactions through compensating REVERSAL records without modifying or deleting historical entries.
- **Balance Management:** Calculating and reconciling account balances using the cumulative financial effects of recorded transactions.
- **Transaction History:** Retrieving historical records through searching, filtering, sorting, and pagination.
- **Financial Reporting:** Generating financial summaries, account activity reports, and expense-category breakdowns.
- **Persistent Storage:** Maintaining application state through a structured local JSON file with an atomic replacement strategy.
- **Data Integrity:** Enforcing monetary precision, transaction validity, account constraints, and persistence consistency.

The application is designed exclusively around the Nigerian Naira (₦), with all internal monetary values represented as integer Kobo.

The system operates within a local, single-user execution environment and does not depend on external banking services or remote infrastructure.

## 1.3 Intended Audience

This specification is intended for individuals involved in the development, testing, evaluation, and maintenance of the Wallet Manager application.

Its primary audiences include:

- **Software Developers:** Responsible for implementing the application's domain models, business workflows, presentation components, and persistence mechanisms.
- **Software Testers:** Responsible for verifying functional correctness, financial calculations, domain invariants, persistence integrity, and expected failure behaviour.
- **Project Evaluators:** Responsible for assessing the completeness, architectural consistency, and technical quality of the proposed implementation.
- **Future Maintainers:** Responsible for understanding existing design decisions, modifying application components, and maintaining compatibility with established business rules.

Readers are expected to have a basic understanding of Python programming, object-oriented design, and conventional software development practices.

## 1.4 Definitions and Terminology

The following terms establish the terminology used throughout this specification.

| Term | Definition |
| --- | --- |
| Wallet Manager | The personal financial management application defined by this specification. |
| SRS | Software Requirements Specification; the formal document describing the system's requirements and constraints. |
| CLI | Command-Line Interface; the text-based interaction mechanism used by the application. |
| Account | A logical financial container used to track available funds. |
| Transaction | A recorded financial event that affects one or more accounts. |
| Ledger | The historical collection of immutable financial transaction records. |
| INCOME | A transaction that increases the balance of a designated account. |
| EXPENSE | A transaction that decreases the balance of a designated account. |
| TRANSFER | An internal movement of funds between two accounts belonging to the same user. |
| REVERSAL | A compensating transaction that negates the financial effect of an eligible original transaction. |
| Kobo | The subdivision of the Nigerian Naira, where 100 Kobo equals ₦1. |
| JSON | JavaScript Object Notation; the structured data format used for persistent application storage. |
| Atomic Replacement | A file replacement operation designed to prevent readers from observing partially written destination files during a successful replacement. |
| Domain Entity | An application object representing a core business concept, such as an Account or Transaction. |
| Business Logic Layer | The application layer responsible for domain validation, financial calculations, and business workflows. |
| Data Access Layer | The application layer responsible for persistent data loading, serialization, and filesystem operations. |
| Presentation Layer | The application layer responsible for terminal interaction and user-facing output. |
| Cached Balance | The stored account balance maintained for efficient access and reconciled against the authoritative transaction ledger. |
| Dependency Injection | A design technique through which application components receive their required dependencies externally rather than constructing concrete dependencies internally. |
| In-Memory State | The application data currently loaded and maintained in active program memory. |
| Persistence | The process of storing application state so that committed records remain available after application termination and reinitialization. |
| Transaction Capacity | The maximum supported number of historical transaction records maintained by the current JSON persistence architecture. |

Unless otherwise stated, technical terms and transaction classifications used throughout this document must be interpreted according to the definitions established above.