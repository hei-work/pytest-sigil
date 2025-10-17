# pytest-sigil

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: ^3.10](https://img.shields.io/badge/python-^3.10-blue.svg)](https://www.python.org/downloads/)

**Proper fixture resource cleanup by handling signals**

A pytest plugin that ensures your test fixtures clean up properly when receiving termination signals (`SIGTERM`),
preventing resource leaks and ensuring graceful shutdowns.


## Problem

When pytest receives a `SIGTERM` signal (e.g., from cancelled CI/CD jobs),
it terminates immediately without running fixture teardown code. This can leave resources dangling:

- Database connections remain open
- Temporary files aren't cleaned up
- Docker containers keep running
- File locks persist

> **Related:** See pytest issues [#5243](https://github.com/pytest-dev/pytest/issues/5243) & [#9142](https://github.com/pytest-dev/pytest/issues/9142) for discussion on this behavior.


## Solution

`pytest-sigil` intercepts `SIGTERM` signals and reroutes them to `SIGINT` handlers, allowing pytest to:

1. Execute fixture teardown code
2. Run cleanup callbacks
3. Exit gracefully with proper status codes

## Installation

```bash
pip install pytest-sigil
```

## Usage

The plugin activates automatically once installed—no configuration needed.

```python
import pytest


@pytest.fixture
def database_connection():
    conn = create_connection()
    yield conn
    conn.close()  # ✓ Now runs even on SIGTERM
```

### Disable the Plugin

If needed, disable it for specific test runs:

```bash
pytest -p no:sigil
```

## CI/CD Configuration

> ⚠️ **Important**: Requires proper signal forwarding in containerized environments. Without an init process, `SIGTERM` won't reach pytest.

### GitLab CI

```yaml
variables:
  FF_USE_INIT_WITH_DOCKER_EXECUTOR: "true"
```

This flag ensures GitLab's Docker executor uses an init process (tini) that properly forwards `SIGTERM` to pytest.
See [GitLab's feature flag documentation](https://docs.gitlab.com/runner/configuration/feature-flags.html#available-feature-flags) for details.

> **Note:** Without proper signal forwarding, the plugin cannot intercept `SIGTERM`. Check your CI provider's documentation for signal handling behavior.

## How It Works

```python
# On session start: SIGTERM → SIGINT
signal.signal(signal.SIGTERM, signal.getsignal(signal.SIGINT))

# On session finish: Restore original SIGTERM handler
signal.signal(signal.SIGTERM, original_handler)
```

This simple rerouting leverages pytest's existing interrupt handling, ensuring all cleanup hooks execute properly.

## License

MIT © [lovetheguitar](https://github.com/hey-works/pytest-sigil)
