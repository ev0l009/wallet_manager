# **9.0 Typing Strategy**

The application must adopt a consistent Python type annotation strategy to improve code readability, maintainability, and early detection of implementation errors.

Type annotations must reflect the established three-tier architecture, domain constraints, and JSON persistence model.

## **9.1 General Typing Requirements**

- All public functions and methods must declare parameter types and return types.
- Internal helper functions should also use type annotations where they improve clarity.
- Domain entities must use explicit field annotations.
- Collections must use appropriate generic types, such as `list[Transaction]` and `dict[str, Account]`.
- Monetary values must be explicitly represented as integers in Kobo.
- Functions returning no meaningful value must use `None` as their return annotation.
- Unrestricted `Any` types should be avoided unless necessary at controlled boundaries, such as handling dynamically loaded JSON data.
- Optional values must be explicitly represented using appropriate optional or union types, such as `str | None`.
- Type annotations must remain consistent across module boundaries.
- Type annotations must not introduce dependencies that violate the established architectural dependency direction.

## **9.2 Domain Model Typing**

- Account types, account statuses, and transaction classifications must use Python `Enum` or `StrEnum` where appropriate.
- Domain entities should use Python `dataclasses` where suitable.
- Transaction entities must be immutable after creation.
- Account entities may be represented as immutable dataclasses to support controlled state replacement through the Business Logic Layer.
- Account metadata changes, including renaming, deactivation, and reactivation, must produce replacement `Account` instances rather than mutate existing instances.
- IDs must be represented consistently as strings.
- Transaction financial dates must use `datetime.date` internally after successful validation.
- Account creation timestamps must use `datetime.datetime`.
- Optional transaction attributes, including category and account references where applicable, must use explicit optional types.
- Domain entity constructors and deserialization methods must enforce their required field types and constraints.

**Enum serialization requirements:**

- Enum values must be converted into JSON-compatible primitive values during serialization.
- Deserialization must reconstruct the appropriate enum members from their persisted values.
- Invalid or unsupported persisted enum values must raise `DataIntegrityError`.
- Persisted enum values must remain consistent with the classifications and account types defined by the application.

## **9.3 Monetary Typing**

- All internal monetary amounts must use Python `int` values representing Kobo.
- `Decimal` must be used only during Naira input parsing and conversion.
- Financial calculations must not use Python `float`.
- Functions performing balance calculations must return integer Kobo values.
- Transaction monetary fields must be annotated as `int`.
- Functions accepting monetary values internally must explicitly expect integer Kobo rather than Naira amounts.
- JSON serialization and deserialization must preserve monetary values as integers.
- Deserialization must reject floating-point and Boolean values where integer monetary values are required.
- Type annotations and documentation must explicitly identify monetary integers as Kobo rather than Naira.

## **9.4 Type Checking Expectations**

- The project should use a static type checker such as `mypy` during development.
- Type-checking errors involving public interfaces, domain entities, and cross-layer dependencies must be resolved before release.
- Type annotations must remain consistent across module boundaries.
- Changes to domain models or the concrete JSON Data Access Layer must be reflected in dependent modules and tests.
- The Data Access Layer must use appropriately typed inputs and outputs when converting between JSON-compatible structures and domain entities.
- Dynamic JSON data must be validated before being treated as typed domain objects.
- Type checking must not be treated as a replacement for runtime validation of user input or persisted data.

---