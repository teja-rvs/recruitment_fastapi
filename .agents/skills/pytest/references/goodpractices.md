# Pytest Good Integration Practices

Source: [Good Integration Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html)

Read this reference when reviewing test layout, collection, import mode, packaging, tox, setuptools test runners, `flake8-pytest-style`, or pytest strict mode.

## Install the package with pip

Prefer a virtual environment plus pip. The project should be installable from `pyproject.toml`.

For development, prefer an editable install so tests and application code can change without reinstalling:

```bash
pip install -e .
```

Report tests that only pass because the repo root is on `sys.path` by accident, rather than because the package is installed.

## Test discovery conventions

If no paths are given, collection starts from `testpaths` (when configured) or the current directory.

Pytest then:

- recurses into directories, skipping `norecursedirs`
- collects files named `test_*.py` or `*_test.py`
- collects `test`-prefixed functions and methods outside a class
- collects `test`-prefixed methods inside `Test`-prefixed classes that have no `__init__`
- also collects `@staticmethod` and `@classmethod` test methods
- also collects `unittest.TestCase` subclasses

Report:

- files that look like tests but will not be collected
- test classes named without a `Test` prefix
- test classes with `__init__`
- helpers accidentally named `test_*`

When collection is in doubt, recommend:

```bash
pytest --collect-only
```

## Prefer tests outside application code

Preferred layout for new projects:

```text
pyproject.toml
src/
    mypkg/
        __init__.py
        app.py
tests/
    test_app.py
```

Benefits:

- tests can run against an installed package after `pip install .`
- tests can run against local code after `pip install -e .`
- application imports are less likely to collide with test modules

Inlining tests inside the package is acceptable when tests should ship with the package:

```text
[src/]mypkg/
    app.py
    tests/
        __init__.py
        test_app.py
```

For inlined tests, recommend:

```bash
pytest --pyargs mypkg
```

Namespace packages can work, but pytest still uses `__init__.py` to decide test package names. Inlined tests should use absolute imports for application code.

## Prefer a `src` layout

A `src/` layout is strongly suggested, especially with the default `prepend` import mode.

This keeps the uninstalled package from being imported accidentally from the repo root.

If there is no editable install and tests must hit the local `src/` tree, `PYTHONPATH=src pytest` or `pythonpath = ["src"]` can work. Prefer an editable install over `PYTHONPATH` when reviewing a maintained application.

If the package lives at the repo root instead of `src/`, `python -m pytest` can import the local copy because the current directory is on `sys.path`. Distinguish this from invoking `pytest` directly; they are not equivalent.

## Prefer `--import-mode=importlib`

Pytest still defaults to `prepend` for historical reasons. For new projects, recommend `importlib`.

```toml
[tool.pytest.ini_options]
addopts = ["--import-mode=importlib"]
```

Pytest 9+ `pytest.toml` equivalent:

```toml
[pytest]
addopts = ["--import-mode=importlib"]
```

Why `importlib` is better:

- pytest does not need to mutate `sys.path` to import tests
- duplicate test module names are allowed (`tests/foo/test_view.py` and `tests/bar/test_view.py`)
- tests are less likely to import the uninstalled local package by accident

`prepend` drawbacks to report:

- test modules must have unique names, because they are imported as top-level modules
- adding `__init__.py` under `tests/` to work around duplicate names prepends the repo root to `sys.path`
- that workaround can make tox test the checkout instead of the installed package

In `prepend`/`append` modes, pytest derives the import name from the first ancestor directory without `__init__.py`. Directory and file names must map to import names.

## tox

Recommend tox when the review is about packaging or CI confidence.

tox should run tests against the installed package, not the source checkout. That is how packaging mistakes are caught.

Report tox configs that put the repo on `PYTHONPATH` or otherwise test the checkout instead of the installed distribution.

## Do not run tests via setuptools

Do not use:

```bash
python setup.py test
```

or `pytest-runner`.

These are deprecated, depend on setuptools features that are going away, and can bypass pip security mechanisms such as `--require-hashes`.

Prefer `pytest`, `python -m pytest`, tox, or the project's chosen test runner.

## flake8-pytest-style

`flake8-pytest-style` can catch fixture, naming, and marker mistakes early.

It is not an official pytest project. Some rules encode style choices, such as `@pytest.fixture()` vs `@pytest.fixture`. Only recommend enabling rules that match the project's style.

## Strict mode

Added in pytest 9.0.

If pytest is pinned or the project wants new strictness options as they appear, recommend:

```toml
[tool.pytest.ini_options]
strict = true
```

Strict mode turns on pytest's strictness options together. Future options will be included.

If the project should not auto-adopt new strictness options, enable them individually:

```toml
[tool.pytest.ini_options]
strict_config = true
strict_markers = true
strict_parametrization_ids = true
strict_xfail = true
```

A single option can be turned off after enabling strict mode:

```toml
[tool.pytest.ini_options]
strict = true
strict_parametrization_ids = false
```

Older projects may already use:

```toml
addopts = [
    "-ra",
    "--strict-markers",
    "--strict-config",
]
```

That is still valid. Prefer `strict = true` when pytest 9+ is in use and pinned.

## Review checklist

- [ ] Package is installed for tests (`pip install -e .` or tox against the installed dist)
- [ ] Tests live in a dedicated `tests/` tree unless inlined tests are intentional
- [ ] `src/` layout is used for application code when practical
- [ ] Collection names follow `test_*.py` / `*_test.py` and `test_` / `Test` conventions
- [ ] `--import-mode=importlib` is used for new projects
- [ ] Duplicate test module names do not rely on `prepend` plus accidental `sys.path` mutation
- [ ] Tests are not run through `python setup.py test` or `pytest-runner`
- [ ] tox, if present, tests the installed package
- [ ] Strict markers/config (or pytest 9 `strict = true`) are enabled when the project can pin pytest
