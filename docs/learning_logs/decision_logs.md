# Final Integration — Full Consolidated Decisions Log

**Assessment:** This file is the reviewer conversation through item 54 (Batch 3b-1). Most of it is **already in the log** from Batches 1 and 2. What's genuinely new:

| New / strengthened | Where it goes |
|---|---|
| **Item 33 — detailed per-layer responsibilities** (what `ui/`, `models/`, `services/`, `file_manager/` each own and explicitly do *not* do) | **Strengthen F1** |
| **Item 49 — the ₦10,000 / ₦8,000 same-day walkthrough** (concrete test case proving the per-context fix) | **Strengthen B6** |
| **Item 50 — the BR-10 insight** ("credits-first ⇒ min running balance = closing balance") | **Strengthen D5** |
| **Item 51 — the split stated as "exception = structure, ui/ = formatting"** | **Strengthen E2** |
| **Item 42 — the arithmetic slip** (`−500,000` kobo = `−₦5,000.00`, not `−₦50.00`) | **Changelog row + debrief item** |
| **Item 22 — failed-save test must include `reactivate`** | **Strengthen F5** |

Everything else in the file is already covered. Below is the fully consolidated log.

---

# Decisions Log — Personal Wallet App

*A reusable record of design decisions from a multi-round review, structured as a guide: **What / Why / How**, plus a dedicated changelog for decisions that were revised, reversed, or superseded.*

---

## How to use this log

- **Section 1** — quick-reference index by category.
- **Section 2** — detailed decision record: what, why, how, limitation for each.
- **Section 3** — the **changelog**: every time the design reversed course, with the reason. Reading *why* a decision changed is more instructive than the decision itself.
- **Section 4** — **reusable process patterns** (meta-lessons).
- **Section 5** — what's still owed, so nothing silently disappears.

---

## 1. Decision Index

| # | Decision | Area | Status |
|---|---|---|---|
| **A. Money** | | | |
| A1 | Integer minor units; never floats | Money | Settled |
| A2 | Central amount parser; one formatter | Money | Settled (parser detail open) |
| A3 | NGN-only display formatter; storage may still carry a code | Money | Settled |
| A4 | Per-currency exponents — principle recorded; v1 NGN-only | Money | Settled |
| **B. Time & Dates** | | | |
| B1 | UTC for audit; user's local zone for "today" | Time | Settled |
| B2 | tz-aware datetimes; truncate to seconds | Time | Settled |
| B3 | Injectable clock: `now_utc()` / `local_today(tz)` | Time | Settled |
| B4 | Future-date rule split: strict on writes, permissive on reads | Validation | Settled |
| B5 | Reversal date system-assigned to `local_today()`; reports consequence stated | Time | Settled |
| B6 | Same-day ordering: account-relative credits before debits; with worked example | Validation | Revised |
| B7 | IANA zone for future schedules (past = UTC; future = wall time + zone) | Time | Settled |
| **C. Account Lifecycle** | | | |
| C1 | Deactivation requires derived balance == 0 | Lifecycle | Settled |
| C2 | Deactivated = excluded from balances, **not** invisible | Lifecycle | Settled |
| C3 | Zero-balance invariant enforced on **every** mutation | Lifecycle | Settled |
| C4 | Name normalization: strip + collapse + casefold uniqueness | Lifecycle | Settled |
| C5 | Rename / deactivate / reactivate on a **clone**, then atomic commit | Lifecycle | Settled |
| C6 | Why account creation stores a timestamp but transactions store a date | Lifecycle | Settled |
| C7 | Check ordering: existence → status → operation-specific → timeline | Lifecycle | Settled |
| **D. Ledger Integrity** | | | |
| D1 | Balance is **derived**, never stored | Ledger | Settled |
| D2 | Append-only ledger; correction = reversal (no edit/delete) | Ledger | Settled |
| D3 | Reversal flips source/target so each row is self-describing | Ledger | Revised |
| D4 | One timeline invariant, one implementation (`validate_account_timeline`) | Ledger | Revised |
| D5 | BR-10 = end-of-day closing balance ≥ 0 per account (with insight) | Ledger | Revised |
| D6 | Transaction field-rules table | Ledger | Settled |
| D7 | Enforcement split: single-record in `models/`, cross-record in `services/` | Ledger | Settled |
| **E. Errors** | | | |
| E1 | Two-branch hierarchy: file/persistence vs. recoverable user action | Errors | Revised |
| E2 | Typed attributes on `DataIntegrityError`; split is "exception = structure, ui/ = formatting" | Errors | Strengthened |
| E3 | Startup wraps `BusinessRuleError` → `DataIntegrityError` | Errors | Settled |
| **F. Architecture & Persistence** | | | |
| F1 | Layering: `ui/ → services/ → file_manager/`; `models/` + `exceptions.py` at base — with per-layer responsibilities | Architecture | Strengthened |
| F2 | JSON at v1 scale; explicit migration trigger | Persistence | Settled |
| F3 | Atomic write: `.tmp` + `flush` + `fsync` + `os.replace` | Persistence | Settled |
| F4 | Startup: three cases, fail fast — **never** fall back to empty (two-stage flow) | Persistence | Revised |
| F5 | Clone-before-mutate; failed-save test covers rename/deactivate/reactivate | Persistence | Strengthened |
| F6 | Storage Protocol deliberately omitted | Persistence | Settled |
| F7 | `WalletEngineData` TypedDict crosses the services ↔ file_manager boundary | Architecture | Settled |
| F8 | Persistence candor: guarantees vs. non-guarantees | Persistence | Settled |
| **G. Schema** | | | |
| G1 | `accounts` = object keyed by ID, `id` omitted inside | Schema | Revised |
| G2 | All enum values lowercase | Schema | Settled |
| G3 | `object_pairs_hook` to catch duplicate keys | Schema | Settled |
| G4 | Sample JSON promoted to a test fixture | Schema | Settled |
| G5 | ID generation: random tokens with type prefixes; regenerate on collision | Schema | Settled |
| **H. Vocabulary** | | | |
| H1 | `INCOME`/`EXPENSE`/`TRANSFER`/`REVERSAL` (retire deposit/withdraw) | Vocabulary | Revised |
| H2 | Spec is authoritative over code drift | Process | Settled |

*(Bold = revised at least once; see Section 3.)*

---

## 2. Detailed Decisions

### A. Money

**A1 — Integer minor units**
- **What:** Store amounts as whole integers in the currency's smallest unit. `1999` + `"USD"` = $19.99.
- **Why:** Exact arithmetic; aligns with payment-processor APIs; no binary-float drift.
- **How:** `BIGINT`/64-bit; `from_dict()` rejects floats and booleans; display conversion only in `ui/`.
- **Limitation:** fractional math (splits, interest, FX) would need explicit decimal rules.

**A2 / A3 — One parser in, one formatter out (NGN-only)**
- **What:** A single `parse_major_to_minor()` at input and a single `format_minor_to_major(amount_minor)` at output. v1 formatter is **NGN-only** (no currency parameter).
- **Why:** Prevents inline `/100` errors; avoids dead multi-currency branches.
- **How:** `utils/formatting.py`; `ui/` calls it for balances, tables, and error messages.
- **Note on storage vs. display:** storage/transmission may still carry a currency code; v1 *display* is NGN. State this explicitly — otherwise A1 ("paired with a code") and A3 ("no currency parameter") look contradictory.
- **Open:** amount **parser** details + **max amount** bound — still owed.

**A4 — Per-currency exponents (principle, v1 NGN-only)**
- **What:** Don't assume 2 decimals. Exponents vary: **0** (JPY, XOF), **2** (USD, NGN, GBP), **3** (KWD, BHD). Keep a currency → exponent mapping.
- **Why:** Hardcoding 100 breaks zero- and three-decimal currencies.
- **How (v1):** Display is NGN-only (A3); the mapping is **not** implemented as runtime branching. Record as design constraint: if a second currency is ever added, the mapping must exist for both storage conversion and display formatting.
- **Limitation:** multi-currency later requires a signature change to the formatter (add `currency`/`exponent` parameter) and per-currency tests.

### B. Time & Dates

**B1 — UTC for audit, local zone for calendar**
- **What:** `created_at` and system logs in tz-aware UTC. "Today" and date filters use the **user's local IANA zone**. Never "timezone or UTC."
- **Why:** UTC is unambiguous global reference; local zone matches human intent for "today." An "or" lets two parts of the system disagree during the UTC-offset overlap hour.
- **How:** `services/` owns conversion; `ui/` never does it.

**B2 — tz-aware datetimes, truncate to seconds**
- **What:** `datetime.now(timezone.utc).replace(microsecond=0)`; `.isoformat(timespec="seconds")` for strings.
- **Why:** `utcnow()` is naive and deprecated; naive/aware comparison raises `TypeError` and catches bugs early. Truncation prevents DB rounding surprises.
- **How / caveat:** Do **not** truncate for high-frequency ordering or profiling.

**B3 — Injectable clock**
- **What:** `now_utc() -> datetime` and `local_today(tz=ZoneInfo("Africa/Lagos")) -> date`.
- **Why:** A rule that reads the system clock is untestable. Injecting `tz` makes date-boundary tests deterministic.
- **How:** `services/` calls these; write validation and report presets both use `local_today()`.

**B4 — Future dates: split the rule by operation**
- **What:** Writes reject `transaction_date > local_today()`. Reads (filters/searches) allow future `end_date`; only reject inverted ranges (`start > end`).
- **Why:** A write is a claim about something that happened; a read filter is just a query window. Rejecting a future `end_date` breaks preset buttons ("This Month", "This Quarter") that legitimately span into the future.
- **How:** Two functions, not one: `validate_transaction_timestamp()` (write) and `validate_search_range()` (read).
- **Limitation:** Optional hardening — clamp `effective_end = min(end, now)` internally for performance; don't 400.

**B5 — Reversal date is system-assigned**
- **What:** `reversal.transaction_date = local_today()`; users cannot backdate it.
- **Why:** A reversal is an **audit event** — it records *when the correction was made*. Historical statements stay intact; the adjustment lands on the day it occurred. Also avoids false rejections when reversing an early INCOME after later expenses.
- **How:** `services/` assigns automatically; `local_today() >= original.transaction_date` is guaranteed by B4.
- **Reports consequence (intended, must be in the spec):** an October expense reversed in November leaves **October's report showing the mistaken expense** (the reversal lands in November). This is the deliberate accounting-audit behavior. A "net of reversals" view is a separate report-level feature — parked.

**B6 — Same-day ordering: account-relative priority (revised, with worked example)**
- **What:** Sort key = `(transaction_date, type_priority, insertion_order)` where `type_priority = 0 if target_acc_id == account_id else 1` — credits are **account-relative**, not transaction-relative.
- **Why:** Transactions store only a calendar **date**, so logging lunch before salary shouldn't reject a valid expense. And on a **transfer**, the same row is an inflow to the destination and an outflow from the source — "credit" must mean "credit *to this account*."
- **Worked example (the bug the fix closes):** Account B receives ₦10,000 by transfer in the morning, spends ₦8,000 at noon, expense logged first.
  - **Old sort (per-type):** `TRANSFER=1, EXPENSE=1` — `insertion_order` decides → expense (−8,000) hits first → running balance −8,000 → **false rejection**.
  - **Fixed sort (per-account direction):** for B, the transfer is an **inflow → priority 0**; expense is **outflow → priority 1**. Sort → `[+10,000, −8,000]` → running 10,000 → 2,000 → **passes.**
- **Why the key is well-defined:** a transaction never has the same account on both sides (TRANSFER has `source ≠ target`; INCOME/EXPENSE/REVERSAL have one side null), so each account sees each row as exactly one of inflow/outflow.
- **Limitation:** assumes same-day inflows precede same-day outflows absent real intra-day timestamps.

**B7 — IANA zone for future schedules**
- **What:**
  - **Past events/logs:** UTC timestamp (ISO 8601 with offset); origin zone stored separately only if local reporting matters.
  - **Future user-facing schedules:** local wall time + IANA zone ID (not a fixed UTC instant).
- **Why:** Governments change DST rules. A fixed UTC instant silently shifts a "9:00 AM" meeting by an hour when rules change. "09:00 + America/New_York" preserves human intent; software recomputes the correct UTC instant with current rules.
- **How:** Separate schemas for the two cases — don't store a future schedule as "just a UTC instant."
- **Limitation:** v1 has no future-schedule feature; this is a **design principle to honor if/when one is added**, not code to write now.

### C. Account Lifecycle

**C1 — Deactivate only at zero balance**
- **What:** Derived balance must be ₦0 before deactivation.
- **Why:** Makes "does a hidden account's money count toward the total?" impossible.

**C2 — Excluded, not invisible**
- **What:** Deactivated accounts are excluded from the default active-balance listing, but visible in a **Deactivated/Archived view** (where they can be reactivated), and **filterable in historical reports**.
- **Why:** Resolves the contradiction "hidden from listing *and* reactivatable." Mirrors real banking: a closed account still needs past history visible.

**C3 — Enforce the invariant on every mutation**
- **What:** Because balance is derived, the zero-balance rule must hold on deactivation **and** on every ledger mutation. Lock ledger writes on inactive accounts.
- **Why:** A one-time check at deactivation is insufficient; a later write would silently break `status == inactive ⇒ balance == 0`.

**C4 — Name normalization (full rule)**
- **What:** `strip()` then collapse internal whitespace runs (`" ".join(name.split())`); uniqueness compared on `casefold()` **across active and inactive accounts**; empty/whitespace-only → `BusinessRuleError`. Renaming to the **exact same normalized name** or **changing only casing** on the same account is **allowed**.
- **Why:** Prevents whitespace/case variants from bypassing uniqueness; keeps reactivation collision-free.
- **How:** Normalize in `services/` before validation; compare `casefold()` against every existing account.
- **Open:** the **length limit** is referenced but not pinned. Recommend **1–100 characters**, documented in the invariant table.

**C5 — Rename / deactivate / reactivate (full rules)**
- **Rename:** exists + active; normalized (C4), non-empty, length-bounded, must not match another account's `casefold()` name; `copy.copy` → set `cloned.name = normalized` → atomic commit.
- **Deactivate:** exists + active; derived balance == 0 required; `copy.copy` → `cloned.deactivate()` → atomic commit; downstream: excluded from active listing; visible in Deactivated view + historical filters; blocked from new transactions/reversals.
- **Reactivate:** exists + inactive; `copy.copy` → `cloned.reactivate()` → atomic commit; restored to main active listing (at preserved ₦0.00); re-enables transactions/reversals.
- **Failed-save test:** rename, deactivate, **and reactivate** each mocked to fail save → assert live instance unchanged (`engine.accounts[id] is original`, original name/status intact).

**C6 — Why account creation stores a timestamp but transactions store a date**
- **What:** Account creation stores an exact tz-aware `datetime` (`created_at`). Transactions store a calendar `date` (`transaction_date`).
- **Why:**
  - **Account creation = system audit event.** Exact timestamps for lifecycle ordering and support tracing. *(v1 has no auth/security — audit/sorting metadata only.)*
  - **Transactions = user-entered business records.** Users log receipts by calendar day, not exact second.
- **How:** tz-aware `datetime` for lifecycle/audit; `date` for transactions. `created_at` does **not** block older `transaction_date` — backdated transactions allowed.
- **Edge case:** a backdated expense must still satisfy the timeline invariant (D5).

**C7 — Check ordering on any account operation**
- **What:** Fixed order:
  1. Existence (`AccountNotFoundError`).
  2. Status (active/inactive as the operation requires).
  3. Operation-specific validation (name uniqueness for rename; balance == 0 for deactivate).
  4. Timeline (for ledger mutations, via `validate_account_timeline()`).
- **Why:** An operation on a **deactivated** account is blocked *before* reversal-date assignment or the timeline check runs. Without a stated order, two code paths can disagree about which error surfaces first.
- **How:** Enforce in `services/` per-operation; document once, cite everywhere.

### D. Ledger Integrity

**D1 — Derived balance**
- **What:** Balance = sum of inflows − outflows, computed from transactions. **No stored/cached balance field.**
- **Why:** Removes an entire class of cache/ledger sync bugs; they can never disagree.
- **Limitation:** O(n) per account read. Fine at ~5,000 transactions with an index on `account_id`; revisit at scale.

**D2 — Append-only, reversal-only correction**
- **What:** Transactions are immutable. The only undo is a new offsetting `REVERSAL` linked to the original.
- **Why:** Preserves a clean financial audit trail.

**D3 — Reversal flips the account fields (revised)**
- **What:** A `REVERSAL` mirrors the original by flipping `source_acc_id`/`target_acc_id`:
  - Reverse an EXPENSE (source = A, target = null) → reversal: source = null, target = A.
  - Reverse an INCOME (source = null, target = A) → reversal: source = A, target = null.
  - Reverse a TRANSFER (A → B) → reversal: B → A.
- **Why:** Every ledger row is **self-describing**. Balance = `sum(target == acc) − sum(source == acc)` — one universal rule, no parent lookup.
- **Bug fixed:** original sample subtracted ₦250 a *second* time instead of refunding (off by ₦500). Corrected sample has `source: null`, `target: A`.

**D4 — One timeline invariant, one implementation (revised)**
- **What:** `validate_account_timeline(account_id, transactions)` in `services/` is the **single** definition. Used by every write (including reversals) **and** by startup's `_validate_chronological_balances()` — which is a **wrapper** that loops all loaded accounts and **delegates**, not duplicates.
- **Why:** A local "current balance ≥ amount" check and a full-timeline check are *not* equivalent. Counterexample: ₦1,000 on Nov 10, reverse ₦1,000 backdated to Nov 5, income ₦1,000 Nov 15 — local check passes, but Nov 5–14 sits at −₦1,000. Collapse to one check.
- **Consequence:** The earlier standalone `balance − amount ≥ 0` sufficiency rule is **removed** (subsumed).

**D5 — BR-10 final wording (with insight)**
- **What (final statement):** Every account's **closing balance at the end of every calendar day** (`opening + day_inflows − day_outflows`) must be **≥ 0 minor units**.
- **The insight that simplified it:** once **credits come first within a day** (B6), the day's **minimum running balance = its closing balance**. So **order among debits cannot change whether that day passes.** BR-10 therefore reduces to the end-of-day rule — the per-transaction walk is equivalent, and preserves the ability to report *which* transaction crossed zero.
- **Single implementation:** `validate_account_timeline(account_id, transactions)` in `services/`. `_validate_chronological_balances()` at startup is a **wrapper** that loops accounts and delegates (D4).
- **Ordering:** sort by `(transaction_date, 0 if target_acc_id == account_id else 1, insertion_order)`.
- **Enforcement:**
  - **Writes** (EXPENSE, TRANSFER, REVERSAL): validate the candidate ledger for **every affected account** before persistence. Any day < 0 → `NegativeBalanceError(account_id, transaction_date, balance)` → abort write.
  - **Startup** (`load_data()`): run the wrapper across every loaded account; convert `NegativeBalanceError` → `DataIntegrityError` **preserving typed attributes** (E2) → halt.
- **Walk-vs-group justification (must be in the spec):** the stated rule is end-of-day closing balance ≥ 0; the implementation uses a sorted per-transaction walk because it **reports which transaction/day crossed zero** (`NegativeBalanceError.transaction_date` = that day; `.balance` = that day's closing balance). A pure group-by-date check reports only the day. `insertion_order` is still required as the **tie-breaker among same-day outflows** and for **stable output ordering in reports**.
- **Limitation (README):** **intra-day overdrafts are permitted** as long as the day closes ≥ 0 — a deliberate consequence of date-only transactions.

**D6 — Transaction field-rules table**

| `trx_type` | `source_acc_id` | `target_acc_id` | `reverses_transaction_id` | Extra invariant |
|---|---|---|---|---|
| `INCOME` | null | required | null | amount > 0 |
| `EXPENSE` | required | null | null | amount > 0; `category` ∈ `ExpCatOpts` |
| `TRANSFER` | required | required | null | source ≠ target; amount > 0 |
| `REVERSAL` | set iff reversing INCOME or TRANSFER; else null | set iff reversing EXPENSE or TRANSFER; else null | required | at least one account set; source ≠ target; amount > 0; `amount == original.amount`; `category = null` |

- **Why:** An invalid `Transaction` **cannot exist in memory** — whether built by a service or loaded from JSON. One table, referenced everywhere.
- **How:** Enforced in `models/`; `from_dict()` raises `DataIntegrityError` on any violation.
- **Limitation:** adding a new `trx_type` requires updating both this table and the enum — a breaking storage change.

**D7 — Enforcement split: single-record vs. cross-record**
- **What:**
  - **Single-record invariants** (D6): enforced inside `Transaction` / `Account` (`__post_init__`, `from_dict()` in `models/`).
  - **Cross-record invariants** (referenced account exists / is active; `reverses_transaction_id` matches original amount; original not already reversed; timeline non-negativity): enforced in `services/`.
- **Why:** Keeps `models/` dependency-free; keeps business rules where the data they need is available.
- **How:** `models/` rejects a structurally invalid record regardless of context; `services/` rejects an operationally invalid one before persistence.
- **Limitation:** a load through `from_dict()` can produce a structurally valid record that is cross-record invalid — `_validate_loaded_data()` catches this at startup (E3/F4).

### E. Errors

**E1 — Two-branch hierarchy (revised)**
```
WalletError
├── StorageReadError     — OS / malformed JSON syntax
├── StorageWriteError    — serialize / fsync / os.replace failure
├── DataIntegrityError   — valid JSON but violates schema/field/timeline
└── BusinessRuleError    — recoverable user action rejected
    ├── InvalidCategoryError
    ├── ReversalError
    ├── AccountNotFoundError
    └── NegativeBalanceError(account_id, transaction_date, balance)
```
- **Why:** `ui/` must distinguish "file damaged — halt" from "action rejected — retry" without guessing from the call site.

**E2 — Typed attributes + "exception = structure, ui/ = formatting" (strengthened)**
- **What:** `DataIntegrityError` carries optional typed fields `account_id`, `transaction_date`, `balance`, populated when `load_data()` converts a `NegativeBalanceError`.
- **The split (explicit):** **exception carries structure; `ui/` builds the human-readable text.** `exceptions.py` cannot import `utils/` (dependency rule), so it holds raw attributes; `ui/` calls `format_minor_to_major(exc.balance)` and renders the account + date.
- **Why:** `.__cause__` is `BaseException | None` — untyped. Typed fields let `ui/` render a clear startup message without importing `NegativeBalanceError`. Building the display text in `ui/` also prevents the startup path from undoing the formatter decision (A2/A3).
- **Note:** `exceptions.py` remains dependency-free.

**E3 — Startup wraps business errors**
- **What:** `from_dict()` catches `BusinessRuleError` + `KeyError`/`TypeError`/`ValueError` → `raise DataIntegrityError(...) from exc`. `WalletEngine.load_data()` wraps `_validate_loaded_data()` and `_validate_chronological_balances()` the same way.
- **Why:** A corrupted file is not a typo; `ui/` should halt, not prompt retry.

### F. Architecture & Persistence

**F1 — Layering (strengthened: detailed per-layer responsibilities)**
- **Canonical layout:** `ui/`, `services/`, `file_manager/`, `models/`, `exceptions.py`, `main.py`. (Folder-based; `file_manager/` name kept for parity with the existing codebase — rename to `storage/` is out of scope for v1.)
- **Dependency flow:** `ui/ → services/ → file_manager/ → JSON`. `models/` + `exceptions.py` sit at the base, imported by all three layers. `file_manager/` never imports `services/` or `ui/`. `main.py` is the composition root.
- **Per-layer responsibilities:**
  - **Presentation (`ui/`):** terminal rendering, `input()` collection, display of errors/confirmations/reports; calls `services/`; **no** financial calculations, **no** direct JSON access, **no** re-implemented business validation; catches expected exceptions (`BusinessRuleError` for retry, `DataIntegrityError` for halt) at operation boundaries.
  - **Core Domain (`models/` + `exceptions.py`):** zero outward deps; defines `Account`, `Transaction`, enums, custom errors; `Account` has **no stored balance**; `Transaction` is **immutable**; entities enforce **single-record field invariants** (D6) + `from_dict()`/`to_dict()`; **cross-entity rules live in `services/`** (D7).
  - **Business Logic (`services/`):** workflows + cross-entity validation (`_validate_loaded_data()`, `_validate_chronological_balances()`); constraints; account lifecycle; transaction ops; **derived** balances; search/filter/sort/pagination/reports; manages proposed in-memory changes; **no** filesystem ops.
  - **Data Access (`file_manager/`):** all disk I/O; JSON (de)serialization (`load_app_data()` + save); `.tmp` + `flush()` + `os.fsync()` + `os.replace()`; structural validation, delegates record reconstruction to `models/` (`from_dict()`); translates FS/serialization failures into `StorageWriteError`/`StorageReadError`; **imports only `models/` + `exceptions.py`**.
- **Why:** Closes the DAL-layering contradiction visibly: `file_manager/` importing `models/` + `exceptions.py` is legal because those are a **separate core**, not "business logic."
- **Limitation:** couples the JSON format to the domain schema — acceptable at v1.

**F2 — JSON at v1, explicit trigger to migrate**
- **What:** Human-readable JSON; advisory target of ~5,000 transactions. Redesign trigger: passing the target, noticeable save latency, or multi-user access → migrate behind the repository interface to SQLite.
- **Why:** Readable, no DB engine/DDL setup, direct mapping to `to_dict()`/`from_dict()`.
- **Correction:** "Zero schema migrations" was **wrong** — a strict `from_dict()` rejects missing/renamed keys, so a v2 field rename needs an explicit migration/upcaster. State this caveat.

**F3 — Atomic write**
- **What:** Write `.storage.json.tmp`, `file.flush()`, `os.fsync(file.fileno())`, then `os.replace()`.
- **Why:** Prevents 0-byte/truncated files on power loss.

**F4 — Startup failure modes (two-stage flow)**
- **What:** Three cases:
  1. No file → clean empty state (create on first save).
  2. Valid file → delete stale `.tmp` (log warning) → parse → `from_dict()` → timeline check → load.
  3. Unreadable/invalid → **halt** with a clear error naming the file/account/date. **Never** fall back to empty.
- **Two-stage flow:**
  1. `file_manager/` — `load_app_data()`: reads `.storage.json`; missing file → empty state; unreadable/malformed JSON or duplicate keys → raises immediately (`StorageReadError` / `DataIntegrityError`).
  2. `services/` — `WalletEngine.load_data()`: calls `load_app_data()`, then `_validate_loaded_data()` (cross-record refs) then `_validate_chronological_balances()` (the wrapper from D4).
  3. Failure at any step → **halt startup**, never fall back to empty.
- **Why:** A failed load + next save = blank-state `os.replace()` over real history → permanent data loss.
- **Note:** The loader **does** run the timeline check. A saved file can never contain a negative dip, so the user is never stuck in a "loads but read-only" state.
- **Calling module:** `services/`, not `file_manager/` — keeps the import rule intact (F1).

**F5 — Clone-before-mutate (strengthened: failed-save test scope)**
- **What:** `services/` shallow-copies the containers (`dict(accounts)`, `list(transactions)`) and clones the target `Account` before applying setter/method. Commits only after `os.replace()` succeeds.
- **Why:** Keeps live state consistent on failed save.
- **Failed-save test (full scope):** mocked to fail save during **rename**, **deactivate**, and **reactivate** — assert live instance unchanged (`engine.accounts[id] is original`, original name/status intact) and `transactions` list unchanged. This is the guarantee that keeps `Account`'s controlled-mutability safe (C5).
- **Limitation:** Relies on consistent cloning — enforced only by the failed-save unit tests.

**F6 — Storage Protocol deliberately omitted**
- **What:** A single JSON backend; no Protocol interface.
- **Why:** Single-backend v1; a Protocol adds boilerplate for no current benefit.
- **How (testing):** `tmp_path`, mock/monkeypatch, or seed `WalletEngineData` directly; **and** a forced-write-failure patch point for the failed-save test (F5).
- **ADR line:** *"Storage Protocol deliberately omitted in v1 … revisit when migrating to SQLite, supporting multiple backends, or exceeding the ~5,000-transaction target."*

**F7 — `WalletEngineData` boundary type**
- **What:** The type crossing the `services/` ↔ `file_manager/` boundary is a **`WalletEngineData` TypedDict** in `models/`:
  ```python
  class WalletEngineData(TypedDict):
      accounts: dict[str, Account]
      transactions: list[Transaction]
  ```
- **Why:** Explicit boundary type; `file_manager/` converts `WalletEngineData` ⇄ `JSONData` via `from_dict()`/`to_dict()`. No bare dicts cross the boundary.
- **Limitation:** the JSON schema and domain schema are coupled (accepted v1 trade-off — see F6).

**F8 — Persistence candor: guarantees vs. non-guarantees**
- **Guarantees:**
  - In-memory state unchanged until successful `os.replace()`.
  - Existing file intact if serialization/staging/fsync fails before replace.
  - Successful replace makes new state visible; failed replace prevents commit.
  - Account changes + ledger additions committed **together**.
  - Transfer reversal persisted as **one** `REVERSAL` row (flipped source/target) in one state update.
- **Does NOT guarantee:**
  - DB-level isolation.
  - Multi-process / concurrent-writer safety.
  - Protection against every hardware failure.
  - Recovery from every OS crash.
  - Automatic rollback after a successful `os.replace()`.
- **Why (candor):** At single-process JSON scale, these are out of scope. Stating them prevents the spec from implying DB-grade guarantees it doesn't have.

### G. Schema

**G1 — Canonical shape**
- **What:** `accounts` = JSON **object keyed by `account_id`**, with `id` **omitted inside** the inner object (no duplicated state). `transactions` = JSON **list**.
- **Why:** Eliminates the "key and inner `id` can disagree" hazard.

**G2 — Lowercase enum values**
- **What:** `AccType`: `bank|cash|savings|mobile`; `AccStat`: `active|inactive`; `TrxType`: `income|expense|transfer|reversal`; `ExpCatOpts`: `food|bills|utilities|transport|healthcare|entertainment|shopping|other`.
- **Limitation:** Renaming an enum `.value` later is a breaking storage change.

**G3 — Duplicate-key protection**
- **What:** `json.load()` silently overwrites duplicate object keys. `file_manager/` passes an `object_pairs_hook` that raises `DataIntegrityError` on any duplicate key.
- **Why:** Preserves the duplicate-ID guarantee even for hand-edited files.
- **Limitation:** Negligible overhead at ~5,000 transactions.

**G4 — Sample as a fixture**
- **What:** Canonical sample JSON lives at `tests/fixtures/valid_sample_storage.json` and is loaded end-to-end in tests.
- **Why:** Prevents sample-vs-rules drift (it drifted 3× before this fix).

**G5 — ID generation & collision handling**
- **What:** IDs are cryptographically random tokens with type prefixes — `secrets.token_urlsafe(...)` or `uuid4()` producing `acc_…` / `trx_…`.
- **Why:** Random tokens avoid guessability, collisions, and the temptation to encode ordering in the ID (the append-only ledger handles ordering via `insertion_order`).
- **How:**
  - **New creation:** check `new_id in store` before insert; **regenerate on collision**. Never `store[new_id] = obj` blindly — that would clobber.
  - **Load:** duplicate IDs in `.storage.json` → `DataIntegrityError`, halt startup (per F4). Duplicate **account** IDs caught while building the dict; duplicate **transaction** IDs caught by a seen-IDs set in `services/`.
- **Limitation:** collision check is linear per creation; negligible at v1 scale.

### H. Vocabulary

**H1 — INCOME / EXPENSE / TRANSFER / REVERSAL (revised)**
- **What:** Retire `deposit`/`withdraw` everywhere (enum, fixture, docs, BR-20).
- **Why (client-language):** "Withdraw ₦20,000 from Main Bank" is a **transfer** (ATM cash → Cash Wallet), not spending. "Deposit cash" is a transfer, not new income. `INCOME`/`EXPENSE` match user intent and make BR-20 natural.

**H2 — Spec is authoritative**
- **What:** When code drifts from the written spec (e.g., `ExpCatOpts` gaining "airtime"), the **spec wins**; change code to match.
- **Why:** Keeps the document the source of truth.

---

## 3. Decision Changelog — Clashes, Reversals, Supersessions

| # | Original | Revised to | Reason | Reusable lesson |
|---|---|---|---|---|
| 1 | **BR-10 Option A**: check *current total* balance ≥ amount | **Option B**: strict chronological running balance ≥ 0 at every date | "Never model spending money before it existed on that date." Counterexample proved the local check passes while a historical window goes negative | A "current total" check and a "whole-timeline" check are **not** the same |
| 2 | **Loader schema-only**; load a negative-dip file and let the user fix it | **Loader runs the timeline check and halts** | A file that loads but blocks every future write is worse than halting | A lenient loader creates a state the write path can't escape |
| 3 | Separate **sufficiency check** `current_balance − amount ≥ 0` | **Removed**; subsumed by `validate_account_timeline()` | Two checks disagreed under backdating | Collapse to one definition, don't add a third |
| 4 | **Reversal keeps original fields**; balance engine negates via parent lookup | **Reversal flips source/target** | Rows become self-describing; one universal balance rule | Prefer **self-contained records** over cross-record lookup for core math |
| 5 | **Same-day order = insertion order only** → **global type priority** → **account-relative priority** | Final: `(transaction_date, 0 if target_acc_id == account_id else 1, insertion_order)` | (a) Date-only transactions: logging lunch before salary shouldn't reject a valid expense. (b) On a transfer, the same row is inflow to destination, outflow from source | When **date-only precision × ordering** interact, fix the **sort key**. When a rule runs **per account**, make the reference point explicit |
| 6 | Money **"paired with an explicit currency code"** everywhere | **NGN-only formatter**; storage may still carry a code | Avoids dead multi-currency code; v1 is NGN | Distinguish **storage/transmission** scope from **display** scope |
| 7 | **Single-module layout** → **Folder layout** (`ui/`, `services/`, `file_manager/`, `models/`, `exceptions.py`, `main.py`) | Folder-based is canonical | Match the actual codebase; one convention everywhere | A **single canonical layout table** referenced everywhere prevents drift |
| 8 | `accounts` as **JSON list** → **dict keyed by ID** → **object keyed by ID, `id` omitted inside** + `object_pairs_hook` | Final: object keyed by ID, `id` omitted inside | Remove duplicated-ID state; guard hand-edited files | One canonical schema section; promote the sample to a fixture |
| 9 | **Single-branch** exception tree | **Two branches**: Persistence/File vs. `BusinessRuleError` | `ui/` must distinguish halt vs. retry without call-site guessing | Error taxonomy should mirror **user recovery actions**, not layers alone |
| 10 | Pass structured details via **`__cause__`** | **Typed optional attributes** on `DataIntegrityError` + "exception = structure, ui/ = formatting" | `.__cause__` is untyped; forces guesswork. And startup text built in `ui/` uses the formatter (A2/A3) | Fix the **type**; keep **presentation** in the presentation layer |
| 11 | "JSON gives **zero schema migrations**" | **Corrected**: strict `from_dict()` requires explicit migration/upcaster | The original claim was false | State trade-offs **honestly** |
| 12 | **`InsufficientFundsError`** | **`NegativeBalanceError(account_id, transaction_date, balance)`** | A backdated write can be rejected while today's balance looks positive; "insufficient funds" would confuse the user | Error names should describe the **rule violated**, not the surface symptom |
| 13 | **Stored/cached balance** on `Account` | **Derived** from transactions | Eliminates an entire class of sync bugs | Remove the cache if consistency matters more than O(n) |
| 14 | Edit/delete transactions | **Append-only; reversal-only** | Audit trail | Prefer immutability + offsetting records over mutation |
| 15 | `deposit`/`withdraw` vocabulary | **`income`/`expense`/`transfer`/`reversal`** | "Withdraw from bank" is a transfer, not spending | Match the **user's** vocabulary |
| 16 | Code decided a category list; spec drifted | **Spec wins**; update `ExpCatOpts` to BR-20 | Keep the document authoritative | Reconcile drift by **changing code to spec** |
| 17 | **Group-by-date check** for BR-10 (equivalent to end-of-day net) | **Sorted per-transaction walk** implementing the same end-of-day rule | Walk reports *which* transaction/day crossed zero; group-by-date reports only the day. Both equivalent given account-relative ordering (B6) | When stated rule and implementation differ in shape, **justify in the spec** |
| 18 | **`StorageReadError` for cross-record issues** | **`DataIntegrityError`** from `services/`, plus startup wrap of `BusinessRuleError` → `DataIntegrityError` | Each error branch maps to a **user recovery action**, not a code path | The class raised depends on the boundary, not just the origin |
| 19 | **Negative amount printed as `−₦50.00`** for `−500000` minor units | **Corrected**: `−500,000` kobo = **`−₦5,000.00`**; single `format_minor_to_major()` used everywhere | Second unit-conversion slip in this project (after the round-1 "$10.50 → 10500 cents" error) | **Hand-verify arithmetic against the formatter**; freeze as a test case |
| 20 | **Startup `str(exc)` printed raw minor units and IDs** | **`ui/` builds display text** from typed attributes via `format_minor_to_major()` | Building the message inside `exceptions.py` would (a) violate the dependency rule and (b) undo A2/A3 on the startup path | When an exception crosses layers, keep **structure in the exception, formatting in `ui/`** |

---

## 4. Reusable Process Patterns

**P1 — Defects live where rules interact.**
Not in single rules but at intersections: reversal × sufficiency, backdating × balance check, loader × invariant, same-day ordering × date-only transactions, transfer reversal × both-endpoint validation. When reviewing a design, deliberately enumerate pairs of rules and ask "what happens at the boundary?"

**P2 — Collapse to one definition; don't add a fourth rule.**
Every time two overlapping checks disagreed, the correct fix was to **delete one** and route both paths through a single implementation (D4). Adding more rules hides the conflict.

**P3 — One implementation, one name.**
Wrapper methods that *call* the single function are fine — but the spec must say so, or "one definition" fractures into two names.

**P4 — Deliver revised text, not intent.**
"I will remove/update X" is treated as intent until the actual section is pasted. Keep a checklist of owed text passages and paste them, not summaries.

**P5 — Hand-verify sample data against the rules.**
The sample JSON drifted from the rules three times before it was promoted to a test fixture. Hand-check field-by-field against every enum and business rule; then freeze it as a fixture so it can't drift again.

**P6 — Spec is authoritative over code drift.**
When code and document disagree, decide *which* is right and propagate in one direction. The default should be "spec wins."

**P7 — Single canonical reference sections.**
Layout table, canonical schema, vocabulary table, error tree — each defined **once**, referenced everywhere. Most "detail contradicts rule" bugs came from restating names per section.

**P8 — Pre-submission pass against earlier sections.**
The "first draft of a detail tends to be written without rereading earlier rules" weakness recurred. Before submitting, re-read all earlier sections for text superseded by the new change.

**P9 — Proposal-first when the reviewer asks.**
If the reviewer says "propose first, I'll respond before further hints," deliver a **standalone proposal**, not the answer embedded in a larger batch. Sequencing matters.

**P10 — Distinguish advisory targets from hard limits.**
"5,000 transactions" is an **advisory performance target**, not a runtime lockout. State the difference so the boundary can't be misread.

**P11 — Separate "storage/transmission" scope from "display" scope.**
The currency-code tension (A1 vs. A3) is an instance of a general pattern: a field may exist in storage but not in display. State both scopes explicitly.

**P12 — Treat structural and business-invariant failures differently from recoverable ones.**
Persistence/file errors → halt. Business-rule errors → retry. Encode this in the exception hierarchy so `ui/` never has to guess.

**P13 — When a rule runs per-account, state the reference point.**
The same transfer row is an inflow to one account and an outflow to another. "Credits before debits" only works if "credit" means "credit *to this account*." Any rule that runs per-entity needs its reference point named.

**P14 — When the stated rule and the implementation differ in shape, justify it in the spec.**
BR-10 states the end-of-day rule, but the implementation uses a sorted per-transaction walk. Fine *only if* the spec explains **why** (the walk reports which transaction/day crossed zero). Leaving the justification only in the log invites the next reader to assume the implementation is wrong.

**P15 — Keep structure in the exception; keep presentation in `ui/`.**
An exception that builds its own message couples it to the formatter, breaks dependency rules, and duplicates formatting logic across the UI. Give it typed fields; let `ui/` decide how to render them.

**P16 — Freeze the arithmetic once; use it everywhere.**
Two unit-conversion slips in one project is the pattern. One tested `format_minor_to_major()` called from every path (UI messages, startup errors, receipts) — no inline `/ 100`.

---

## 5. Still Open (for continuity)

**Design items still owed:**
- **Name length limit** — recommend 1–100 characters, documented in the invariant table.
- **Amount parser + max amount** — longest-outstanding. Pin the source (int64? JSON-integer? persistence bound?).
- **Invariants table** — consolidate D5 (timeline), D6 (transaction field rules), C1–C3 (lifecycle), C4 (name rules + length), C7 (check ordering) in **one table** using final vocabulary.

**Gate 1 (after the above):**
- **Testing strategy** — clock injection point (how tests make "now" be 11:30 pm UTC on a chosen date), plus **invalid fixtures** (duplicate key, negative timeline, bad category) — a valid fixture only proves acceptance, not rejection.
- **Full exception tree in the spec** — including `AccountNotFoundError` and the `__post_init__` validation error for user input (zero amount → a `BusinessRuleError`-family validation error, **not** `DataIntegrityError`). Pin its base class.
- **Out-of-scope list** — including the file-format version field decision.
- **Error-handling strategy** — state the scope of the `try` in `from_dict()` (catching `ValueError`/`TypeError` around the whole body would report your own bugs as a corrupt file).

**Parked:**
- **Report treatment of reversal pairs** — B5 decided *which period*; display rule (show pair together? net?) remains parked.

**Documentation owed:**
- **README** — category boundary (bills vs. utilities), intra-day overdraft permission, recovery from invalid files, `ZoneInfo("Africa/Lagos")` timezone-database dependency.
- **Spec text owed** — the walk-vs-group justification in §BR-10; the `insertion_order` defence in §BR-10; the BR-10 → reports consequence in §5 or §6; the `WalletEngineData` boundary type in §6.1/§6.4; the per-layer responsibilities in §5.1.

**Process notes for the debrief:**
- Unit-conversion slips ×2 (`$10.50`; `−₦50.00`) — both self-caught on hand-verification.
- Code-over-spec drift ×3 (categories, hierarchy, formatter).
- Loader-leniency reversal (self-corrected).
- Sequencing miss on the `NegativeBalanceError` proposal (delivered inside a batch rather than standalone — substance fine, process noted).
- Addendum-vs-earlier-section drift (once caught; mitigation now in place via canonical tables).
- Per-type-where-per-context (same-day ordering; fixed and demonstrated).