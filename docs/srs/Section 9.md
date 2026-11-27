# 9.0 Typing Strategy

The application must adopt a consistent Python type annotation strategy to improve code readability, maintainability, and early detection of implementation errors.

## 9.1 General Typing Requirements

- All public functions and methods must declare parameter types and return types.
- Internal helper functions should also use type annotations where they improve clarity.
- Domain entities must use explicit field annotations.
- Collections must use appropriate generic types.
- Monetary values must be explicitly represented as integers in Kobo.
- Functions returning no meaningful value must use `None` as their return annotation.
- Unrestricted `Any` types should be avoided unless necessary.
- Optional values must be explicitly represented using appropriate optional or union types.

## 9.2 Domain Model Typing

- Account types, account statuses, and transaction classifications must use Python `Enum` or `StrEnum` where appropriate.
- Domain entities should use Python `dataclasses` where suitable.
- Transaction entities should be immutable after creation.
- Account entities may support controlled state changes through validated domain operations.
- IDs must be represented consistently as strings.
- Transaction dates must use `datetime.date` internally after successful validation.
- Account creation timestamps must use `datetime.datetime`.

## 9.3 Monetary Typing

- All internal monetary amounts must use Python `int` values representing Kobo.
- `Decimal` must be used only during Naira input parsing and conversion.
- Financial calculations must not use Python `float`.
- Functions performing balance calculations must return integer Kobo values.
- Type annotations and documentation must explicitly identify monetary integers as Kobo rather than Naira.

## 9.4 Type Checking Expectations

- The project should use a static type checker such as `mypy` during development.
- Type-checking errors involving public interfaces and domain entities must be resolved before release.
- Type annotations must remain consistent across module boundaries.
- Changes to domain models or storage interfaces must be reflected in dependent modules and tests.

---