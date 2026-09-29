---
name: pytest-review
description: Pytest standards review. Use when reviewing existing Python test files, test directories, conftest.py files, fixtures, markers, parametrized tests, async tests, mocking, monkeypatching, and test isolation. Also use when reviewing test layout, collection, import mode, src layout, tox, pytest strict mode, or pytest good integration practices. Reviews only Pytest patterns and anti-patterns. Does not review FastAPI application code or production code unless directly needed to understand a test.
---

# Pytest Review

Use this skill when the user asks to review, audit, or check Pytest code for standards, correctness, maintainability, and test isolation.

This skill is Pytest-only. It is not a general Python linting skill, not a FastAPI application design skill, and not a production-code review skill.

## Invocation

```text
/pytest-review <file-or-directory>
```

Examples:

```text
/pytest-review tests/test_users.py
/pytest-review tests/
/pytest-review tests/conftest.py
```

If no target is provided, ask the user which Pytest file or directory should be reviewed.

## Scope

Only review Pytest-related code:

- `test_*.py` files
- `*_test.py` files
- `conftest.py` files
- Pytest fixtures
- Pytest markers
- Pytest parametrize usage
- Pytest plugins used by the tests
- Test configuration directly affecting Pytest
- Test layout, collection, import mode, and pytest strictness options

Do not review:

- FastAPI route design
- production architecture
- database schema design
- application performance
- frontend code
- unrelated Python style preferences

You may look at production code only when it is directly necessary to understand a fixture, dependency override, mock, or assertion.

When reviewing tests for a FastAPI application, only comment on the Pytest side:

- test client fixtures
- async test handling
- dependency override usage in tests
- fixture isolation
- assertions on responses
- test data setup and teardown

Do not rewrite FastAPI application code unless explicitly asked.

## Review Goal

Determine whether the tests follow standard Pytest conventions and whether they are:

- deterministic
- isolated
- readable
- maintainable
- correctly collected
- correctly scoped
- correctly async-handled
- free of common Pytest anti-patterns

## Review Checklist

Check for the following issues.

### 1. Incorrect fixture usage

Look for:

- fixtures used as regular functions
- fixtures imported manually instead of discovered through `conftest.py`
- fixtures doing unrelated work
- fixtures returning large complex objects when a factory would be clearer
- fixtures mutating shared state
- fixtures depending on hidden global state
- fixtures used outside their intended scope

Prefer fixtures that are small, explicit, composable, and reusable.

For request rules, caching, factories, parametrized fixtures, `usefixtures`, overrides, and `pytest_plugins`, read [references/fixtures.md](references/fixtures.md).

### 2. Missing or incorrect fixture teardown

Look for fixtures that create resources but do not clean them up.

Prefer `yield` fixtures for setup and teardown:

```python
import pytest


@pytest.fixture
def db_session():
    session = create_session()
    yield session
    session.close()
```

If cleanup must be guaranteed, use `try/finally`:

```python
import pytest


@pytest.fixture
def db_session():
    session = create_session()
    try:
        yield session
    finally:
        session.close()
```

Prefer one state-changing action per fixture, with teardown next to that action. A single yield fixture that creates several resources will skip all teardown if setup fails before `yield`.

Report missing teardown when fixtures create:

- database sessions
- HTTP clients
- temporary directories outside `tmp_path`
- background tasks
- environment mutations
- global state mutations
- external service connections

### 3. Fixture scope misuse

Default to function-scoped fixtures. Valid scopes are `function`, `class`, `module`, `package`, and `session`.

A fixture may request a broader fixture. A session-scoped fixture must not request a module- or function-scoped fixture.

Only widen scope when the resource is:

- expensive to create
- safe to share
- immutable or effectively immutable
- not affected by test execution order

Report suspicious use of:

```python
@pytest.fixture(scope="session")
```

or:

```python
@pytest.fixture(scope="module")
```

when the fixture returns mutable state that tests can modify.

Good session-scoped examples:

- read-only configuration
- compiled templates
- static test data
- expensive immutable clients

Bad session-scoped examples:

- mutable database state shared by tests
- user factories with shared counters
- dictionaries or lists mutated by tests
- environment variable state modified by tests

### 4. Overuse of session/module scope fixtures

Report when session or module scope is used for convenience rather than necessity.

Prefer:

```python
@pytest.fixture
def user_factory():
    return make_user
```

over a shared mutable object:

```python
@pytest.fixture(scope="session")
def users():
    return [make_user(), make_user()]
```

unless the object is truly immutable and expensive to create.

### 5. Test order dependencies

Tests must pass in any order.

Look for:

- reliance on data created by earlier tests
- global variables mutated by tests
- module-level dictionaries or lists mutated by tests
- environment variables changed without restoration
- database rows created and not cleaned
- files written to shared locations
- tests expecting another test to run first

Recommend:

- `pytest-randomly` for detecting order dependence
- factory fixtures instead of shared state
- `monkeypatch` for environment and attribute mutation
- `tmp_path` for filesystem isolation

### 6. Shared state leakage

Report any shared mutable state that can leak between tests.

Common sources:

- module-level variables
- class attributes mutated in tests
- session-scoped mutable fixtures
- global caches
- singletons mutated by tests
- environment variables
- `sys.modules`
- `sys.path`
- current working directory changes

Prefer scoped cleanup through:

- fixtures
- `monkeypatch`
- `tmp_path`
- context managers
- explicit teardown

### 7. Incorrect use of `pytest.mark.parametrize`

Check that parametrized tests are clear, deterministic, and readable.

Prefer tuple argument names:

```python
import pytest


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (1, True),
        (0, False),
    ],
)
def test_is_positive(value, expected):
    assert is_positive(value) is expected
```

Report:

- unclear parameter names
- large inline data sets with no IDs
- generated parameter values that make test IDs unreadable
- missing IDs when values are objects or complex structures
- parametrize data that mutates during test execution
- excessive parametrize combinations causing slow test suites

Use explicit IDs when useful:

```python
import pytest


@pytest.mark.parametrize(
    ("email", "expected"),
    [
        pytest.param("user@example.com", True, id="valid-email"),
        pytest.param("invalid", False, id="missing-at-sign"),
    ],
)
def test_validate_email(email, expected):
    assert validate_email(email) is expected
```

### 8. Missing test IDs where useful

Report missing IDs when parametrize cases are hard to distinguish.

Bad:

```python
@pytest.mark.parametrize(
    ("payload", "expected_status"),
    [
        ({}, 422),
        ({"name": "x"}, 201),
    ],
)
def test_create(payload, expected_status):
    ...
```

Better:

```python
@pytest.mark.parametrize(
    ("payload", "expected_status"),
    [
        pytest.param({}, 422, id="empty-payload"),
        pytest.param({"name": "x"}, 201, id="valid-payload"),
    ],
)
def test_create(payload, expected_status):
    ...
```

Only require IDs when they improve clarity. Do not make IDs mandatory for trivial cases.

### 9. Too-broad `pytest.raises`

Report overly broad exception catching.

Bad:

```python
import pytest


def test_fails():
    with pytest.raises(Exception):
        do_something()
```

Better:

```python
import pytest


def test_fails():
    with pytest.raises(ValueError):
        do_something()
```

Use `match` when the exception message matters:

```python
import pytest


def test_invalid_email():
    with pytest.raises(ValueError, match="invalid email"):
        parse_email("not-an-email")
```

Do not require `match` for every exception. Use it when the message is part of the observable behavior.

### 10. Multiple statements inside `pytest.raises`

The block should contain only the statement expected to raise.

Bad:

```python
import pytest


def test_create_user():
    with pytest.raises(ValueError):
        user = build_user()
        save_user(user)
        notify_admin(user)
```

Better:

```python
import pytest


def test_create_user():
    user = build_user()

    with pytest.raises(ValueError):
        save_user(user)

    notify_admin(user)
```

Report cases where unrelated setup, mutation, or assertions are inside `pytest.raises`.

### 11. unittest-style assertions

Prefer plain Pytest assertions.

Report usage like:

```python
self.assertEqual(result, expected)
self.assertTrue(flag)
self.assertIn(item, items)
```

Prefer:

```python
assert result == expected
assert flag is True
assert item in items
```

Pytest supports plain `assert` with detailed failure introspection.

### 12. Weak assertions

Report assertions that do not meaningfully verify behavior.

Examples:

```python
assert response
```

```python
assert result is not None
```

```python
assert "id" in data
```

These may be acceptable in limited cases, but report them when the test should be asserting a more specific behavior.

Prefer assertions that verify observable behavior:

```python
assert result.id == expected_id
assert response.status_code == 201
assert data["email"] == payload["email"]
```

For floating-point comparisons, recommend:

```python
import pytest


assert value == pytest.approx(0.1 + 0.2)
```

### 13. Tests that do not actually assert meaningful behavior

Report tests that:

- only check that no exception was raised
- only check truthiness
- only check type without checking content
- call code but never assert results
- assert constants
- assert the mock was called without explaining why that matters
- test implementation details instead of behavior

Prefer tests that verify observable outcomes:

- return values
- raised exceptions
- state changes
- emitted events
- recorded logs
- HTTP response status and body
- side effects through test doubles

### 14. Unused fixtures

Report fixtures that are defined but not used.

If unsure whether a fixture is used indirectly through `conftest.py` or plugin hooks, classify the issue as a suggestion instead of an error.

### 15. Duplicated fixtures

Report duplicated fixture logic when the same setup appears in multiple places.

Recommend:

- moving shared fixtures to the nearest appropriate `conftest.py`
- creating a factory fixture
- parametrizing the fixture
- using `request.param` for fixture variants

Example:

```python
import pytest


@pytest.fixture(params=["admin", "user"])
def role(request):
    return request.param
```

### 16. Missing markers or unregistered markers

Report markers that are used but not registered.

Recommend configuration like:

```toml
[tool.pytest.ini_options]
markers = [
    "unit: unit tests",
    "integration: integration tests",
    "slow: slow tests",
]
```

Also recommend strict marker checking:

```toml
[tool.pytest.ini_options]
addopts = [
    "-ra",
    "--strict-markers",
    "--strict-config",
]
```

Report misspelled or inconsistent markers such as:

- `unit`
- `units`
- `unit-test`
- `integration`
- `integ`

### 17. Incorrect async test handling

For async tests, ensure the project uses a consistent async Pytest plugin, usually one of:

- `pytest-asyncio`
- `anyio`
- `trio` via Pytest plugin

Report:

- async test functions without an async plugin configured
- manual use of `asyncio.run()` inside tests
- manual event loop fixtures when unnecessary
- mixing async and sync fixture patterns incorrectly
- async fixtures not awaited or not defined correctly
- unclear async mode configuration

For `pytest-asyncio`, prefer explicit configuration.

Strict mode:

```toml
[tool.pytest.ini_options]
asyncio_mode = "strict"
```

Then mark async tests explicitly:

```python
import pytest


@pytest.mark.asyncio
async def test_example():
    assert True
```

Auto mode:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

Auto mode is acceptable if the project intentionally uses it, but report it as a suggestion if the mode is unclear or inconsistent.

Do not recommend manually creating event loops inside tests.

### 18. Tests that are not correctly named or may not be collected

Check that test files and test functions follow standard collection rules.

Standard file names:

```text
test_users.py
users_test.py
```

Standard function names:

```python
def test_create_user():
    ...
```

Report:

- files not matching `test_*.py` or `*_test.py`
- functions not prefixed with `test_`
- test classes with `__init__`
- test helper functions accidentally named like tests
- fixtures accidentally named like tests
- async tests that may not be collected due to missing plugin configuration

If collection behavior depends on project configuration, recommend checking:

```bash
pytest --collect-only
```

For layout, import mode, `src/` vs inlined tests, tox, and strict mode, read [references/goodpractices.md](references/goodpractices.md).

### 19. Poor test layout or import mode

Read [references/goodpractices.md](references/goodpractices.md) before commenting on packaging or collection mechanics.

Report:

- application code importable from the repo root by accident instead of via an editable or tox install
- missing `src/` layout when `prepend` import mode makes local imports easy to get wrong
- default `prepend` import mode on a new project instead of `importlib`
- duplicate test module names that only work because `tests/` was added to `sys.path`
- `__init__.py` files added under `tests/` only to allow duplicate names, which can make tox test the checkout
- `python setup.py test` or `pytest-runner`
- tox configs that test the source tree instead of the installed package

Prefer:

```toml
[tool.pytest.ini_options]
addopts = ["--import-mode=importlib"]
```

and an editable install:

```bash
pip install -e .
```

### 20. Fixture sharing, overrides, and `usefixtures`

Read [references/fixtures.md](references/fixtures.md).

Report:

- importing fixture functions instead of discovering them or using `pytest_plugins`
- `@pytest.mark.usefixtures` on a fixture function (invalid; request the other fixture as a parameter)
- factories that create resources and never destroy them
- parametrized fixtures with unclear IDs for objects
- accidental same-name fixture overrides in nested `conftest.py` files
- session fixtures depending on narrower fixtures

## Additional Pytest Standards

### Prefer plain `assert`

Pytest's plain `assert` is preferred over helper assertion methods.

Good:

```python
def test_total():
    assert calculate_total([10, 5]) == 15
```

### Prefer `monkeypatch` for scoped mutation

Use `monkeypatch` for changing:

- environment variables
- attributes
- dictionary items
- `sys.path`
- module-level functions
- imports

Example:

```python
def test_debug_mode(monkeypatch):
    monkeypatch.setenv("DEBUG", "true")
    assert is_debug_enabled() is True
```

`monkeypatch` automatically restores state after the test.

Report manual patterns like:

```python
import os


def test_debug_mode():
    os.environ["DEBUG"] = "true"
    assert is_debug_enabled() is True
```

unless the environment variable is restored during teardown.

### Prefer `tmp_path` for filesystem tests

Good:

```python
def test_write_file(tmp_path):
    file_path = tmp_path / "output.txt"
    file_path.write_text("hello")
    assert file_path.read_text() == "hello"
```

Report hardcoded temporary paths such as:

```python
path = "/tmp/output.txt"
```

unless there is a clear reason and proper cleanup.

### Prefer explicit test markers for slow or integration tests

Example:

```python
import pytest


@pytest.mark.slow
def test_large_report():
    ...
```

```python
import pytest


@pytest.mark.integration
def test_database_connection():
    ...
```

Markers allow selective execution:

```bash
pytest -m "not slow"
```

### Avoid `print` debugging in tests

Report `print` used for debugging.

Recommend:

```bash
pytest -s
```

or using `capsys`, `caplog`, or debugger breakpoints.

### Avoid `time.sleep`

Report `time.sleep` in tests unless the test is explicitly testing timing behavior.

Prefer:

- polling with timeout
- fake time
- deterministic test doubles
- event-driven synchronization
- async wait primitives when appropriate

### Avoid autouse fixtures unless necessary

Autouse fixtures can hide dependencies.

Report autouse fixtures unless they are truly required for every test in scope.

Bad pattern:

```python
import pytest


@pytest.fixture(autouse=True)
def setup_everything():
    ...
```

Better when possible:

```python
import pytest


@pytest.fixture
def api_client():
    ...
```

Then explicitly request the fixture in tests that need it.

A class-scoped autouse fixture is acceptable when it is the **act** step for several read-only asserts after expensive setup. Keep that autouse on the class that needs that scenario, not on the whole module.

### Prefer factories over shared test data

Bad:

```python
USER = {"id": 1, "name": "Alice"}


def test_user():
    assert USER["id"] == 1
```

Better:

```python
def make_user(**overrides):
    user = {"id": 1, "name": "Alice"}
    user.update(overrides)
    return user


def test_user():
    user = make_user(name="Bob")
    assert user["name"] == "Bob"
```

Factories reduce shared-state leakage.

### Prefer one behavior per test

Each test should verify one primary behavior.

Bad:

```python
def test_user():
    test_create_user()
    test_update_user()
    test_delete_user()
```

Better:

```python
def test_create_user():
    ...


def test_update_user():
    ...


def test_delete_user():
    ...
```

### Prefer clear Arrange-Act-Assert structure

Good:

```python
def test_apply_discount():
    # Arrange
    price = 100
    discount = 10

    # Act
    total = apply_discount(price, discount)

    # Assert
    assert total == 90
```

Report tests where setup, behavior, and assertions are tangled.

## Recommended Pytest Configuration

When relevant, recommend this baseline configuration:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "-ra",
    "--import-mode=importlib",
    "--strict-markers",
    "--strict-config",
]
markers = [
    "unit: unit tests",
    "integration: integration tests",
    "slow: slow tests",
]
```

On pytest 9+ with a pinned pytest version, prefer `strict = true` instead of listing each strictness flag. Details are in [references/goodpractices.md](references/goodpractices.md).

## References

Read only the files needed for the current review:

- Test layout, collection, import mode, packaging, tox, setuptools runners, `flake8-pytest-style`, and strict mode: [references/goodpractices.md](references/goodpractices.md)
- Fixtures (requesting, scope, teardown, factories, parametrization, `usefixtures`, overrides, plugins): [references/fixtures.md](references/fixtures.md)

Upstream:

- [Good Integration Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html)
- [How to use fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
   