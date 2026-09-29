# How to Use Fixtures

Source: [How to use fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)

Read this reference when reviewing fixture request patterns, scope, teardown, factories, parametrized fixtures, `usefixtures`, fixture overrides, or sharing fixtures across projects.

Also see [About fixtures](https://docs.pytest.org/en/stable/explanation/fixtures.html) and the [Fixtures reference](https://docs.pytest.org/en/stable/reference/fixtures.html).

## Request fixtures by argument name

Tests request fixtures by declaring them as parameters. Pytest matches those names, runs the fixtures, and injects the return values.

Fixtures request other fixtures the same way. Prefer small, composable fixtures over one fixture that does everything.

Do not call fixture functions as ordinary Python functions. Report:

```python
def test_user(user):
    extra = user()  # fixture used as a function
```

A fixture's return value is cached for the test. If several fixtures and the test request the same fixture, pytest runs it once and reuses that object, including side effects.

Function-scoped fixtures give each test its own result. That is the default isolation model.

## Do not import fixtures

Fixtures should be discovered from `conftest.py`, plugins, or `pytest_plugins`.

Do not import fixture functions into a test module. Importing registers them as defined in the importing module. That can duplicate them in `pytest --help` and may break in future pytest versions.

To reuse fixtures from another package that is not a pytest plugin:

```python
# app/tests/conftest.py
pytest_plugins = "mylibrary.fixtures"
```

Prefer installing projects that expose fixtures via entry points.

## Autouse fixtures

`autouse=True` makes every test in scope request the fixture without naming it.

Use autouse sparingly. Hidden setup is hard to review.

Legitimate uses:

- a narrow, local side effect that every test in that class or module needs
- a class-scoped **act** fixture so several tests can assert different outcomes of one setup (see multiple asserts below)

Report module- or session-wide autouse that is not obviously required by every test.

## Scope

Created on first request; destroyed according to `scope`:

| Scope | Destroyed |
| --- | --- |
| `function` (default) | end of the test |
| `class` | teardown of the last test in the class |
| `module` | teardown of the last test in the module |
| `package` | teardown of the last test in the package that defines the fixture, including subpackages |
| `session` | end of the session |

Widen scope only for expensive, safe-to-share resources.

A fixture may request a **broader** fixture (`module` may use `session`). A session-scoped fixture must not request a module- or function-scoped fixture.

Pytest caches one instance of a fixture at a time. A parametrized fixture may still run more than once inside its scope.

Dynamic scope (pytest 5.2+): `scope` may be a callable `(fixture_name, config) -> str`. Use this when CLI flags should change scope, for example keeping Docker containers for a session.

## Yield fixtures (preferred teardown)

Prefer `yield` over `return` when cleanup is needed. Setup runs before `yield`; teardown runs after, in reverse setup order.

If a yield fixture raises **before** yielding, pytest does not run that fixture's teardown. Fixtures that already yielded still tear down.

```python
@pytest.fixture
def sending_user(mail_admin):
    user = mail_admin.create_user()
    yield user
    mail_admin.delete_user(user)
```

`request.addfinalizer` is the more verbose alternative. Finalizers run even if the fixture later raises, so register the finalizer **after** the resource exists.

Yield teardown order: last requested fixture first (right-most argument). `addfinalizer` is first-in, last-out.

## Safe teardowns: one state change per fixture

Do not pack create-user, send-email, and delete-users into one yield fixture. If setup fails mid-way, teardown after `yield` never runs.

Prefer one state-changing action per fixture, bundled with its own teardown. Independent resources (user vs browser) can be separate fixtures even if order is not obvious.

Report fixtures named `setup` that return tuples of unrelated objects.

## Multiple asserts after expensive setup

When one action should be checked several ways, a class-scoped autouse **act** fixture can run once, then each test method asserts one outcome.

Keep those tests read-only after the act. Put the act fixture on the class that needs that scenario, not on the whole module.

This is not a license for shared mutable class state. Prefer pytest fixtures over `unittest.TestCase` instance state.

## Introspect the request

Fixtures may take `request` (`FixtureRequest`) to read the calling test, class, or module.

```python
server = getattr(request.module, "smtpserver", "smtp.gmail.com")
```

Markers can pass data into a fixture:

```python
marker = request.node.get_closest_marker("fixt_data")
```

If the marker is optional, handle a missing marker. Register custom markers.

## Factories as fixtures

When a test needs several instances, return a factory function instead of one object.

If the factory creates resources, the fixture must track and tear them down:

```python
@pytest.fixture
def make_customer_record():
    created = []

    def _make(name):
        record = models.Customer(name=name)
        created.append(record)
        return record

    yield _make
    for record in created:
        record.destroy()
```

Report factories that create DB rows, files, or users with no cleanup.

## Parametrizing fixtures

`@pytest.fixture(params=[...])` reruns dependent tests for each value. Read the value from `request.param`. Downstream fixtures do not need to know about the parametrization.

Pytest builds IDs such as `test_ehlo[smtp.gmail.com]`. Numbers, strings, booleans, and `None` stringify normally; other objects get weaker IDs. Prefer `ids=` (list or callable). A callable may return `None` to keep the auto ID.

Apply marks to individual params with `pytest.param(value, marks=pytest.mark.skip)`.

Pytest groups tests to minimize live fixture instances: it finishes one parametrized instance (and its teardown) before creating the next.

## `usefixtures`

Use `@pytest.mark.usefixtures("cleandir")` when the test needs the fixture's **side effect** but not its return value. Works on tests, classes, `pytestmark`, or config `usefixtures = [...]`.

**Error:** `@pytest.mark.usefixtures` on a fixture function does nothing useful and is invalid. A fixture that needs another fixture should request it as a parameter.

Prefer `tmp_path` over hand-rolled `os.chdir` plus `tempfile` unless the test must change the process working directory.

## Overriding fixtures

Same-named fixtures can override at:

- a subdirectory `conftest.py`
- a test module
- `@pytest.mark.parametrize("username", [...])`, even if the test does not request `username` directly but a fixture does

The override may request the original fixture as a parameter (`def username(username):`).

A parametrized fixture can be overridden by a non-parametrized one, and the reverse.

Report accidental overrides (duplicate fixture names in nested conftests) and intentional overrides that no longer call the parent fixture when they should.

## Review checklist

- [ ] Fixtures are requested by argument name, not called or imported
- [ ] Cross-project fixtures use plugins or `pytest_plugins`, not imports
- [ ] Autouse is justified and scoped tightly
- [ ] Scope matches cost and mutability; narrower fixtures do not feed session fixtures
- [ ] Resource fixtures yield and tear down; one state change per fixture
- [ ] Factories that create resources clean them up
- [ ] Parametrized fixtures use `request.param` and readable `ids` when needed
- [ ] `usefixtures` is not applied to fixture functions
- [ ] Fixture overrides in nested conftests/modules are intentional
