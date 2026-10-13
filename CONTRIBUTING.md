# Contributing

Thanks for your interest in contributing to `engineering-format`.

## Development setup

The project uses Python 3.12 or newer and `uv`. From the repository root, install the development dependencies with:

```bash
uv sync --group dev
```

## Checks

Run the linter and test suite before opening a pull request:

```bash
uv run ruff check .
uv run pytest
```

CI runs these checks on Python 3.12, 3.13, 3.14, and 3.15.

## Changes

- Add or update tests when changing formatting or parsing behavior.
- Update the README and its runnable examples when changing documented behavior. You can run the examples with `uv run python examples/readme_examples.py`.
- Keep changes focused and compatible with the project's supported Python versions.

Pull requests should briefly explain the change and note any relevant testing performed.

## Creating a release

Releases are created by pushing a version tag. After the release changes are merged to `main`:

1. Choose the next version and update the project version:

	```bash
	uv version X.Y.Z
	uv lock
	```

2. Run the checks listed above, then commit the version and lockfile changes:

	```bash
	git add pyproject.toml uv.lock
	git commit -m "Release vX.Y.Z"
	```

3. Tag that commit and push the branch and tag:

	```bash
	git tag vX.Y.Z
	git push origin main --tags
	```

The `v*` tag triggers the release workflow. It verifies that the tag matches the project version, runs lint and tests, builds the distributions, publishes them to PyPI, and creates a GitHub release with generated notes and the distribution files. Check the workflow run to confirm the release completed successfully.