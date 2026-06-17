# Contributing to Hot Take Tracker

Thank you for considering contributing. Please read the project README to understand the architecture before making changes.

## Development Setup

1. Follow the Quick Start instructions in README.md.
2. Run the test suite before opening a PR:
   ```bash
   cd backend
   python -m pytest tests/ -v
   ```
3. Ensure the frontend builds without errors:
   ```bash
   cd frontend
   npm run build
   ```

## Code Standards

- No placeholder functions, no TODO comments, no bare `except` clauses.
- No `print()` -- use the `logging` module.
- Every frontend component must be under 200 lines and handle all states (loading, error, empty, success).
- Every new API endpoint must have a corresponding hermetic test.
- Tests must not require live Walrus, OpenAI, or network access.

## Pull Request Process

1. Keep PRs focused on a single concern.
2. Include or update tests for any changed behavior.
3. Verify all existing tests still pass.
4. Link any related issues in the PR description.

## Reporting Issues

Use the GitHub issue tracker. Include:
- A clear, descriptive title.
- Steps to reproduce (for bugs).
- Expected vs. actual behavior.
- Relevant logs or error messages (with sensitive data redacted).
