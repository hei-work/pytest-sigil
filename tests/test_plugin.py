"""Tests for the pytest plugin behavior."""

import signal
import sys
import time
from importlib import metadata

import pytest

import pytest_sigil

pytest_plugins = ["pytester"]


def test_plugin_is_loaded_in_current_pytest_session(
    pytestconfig: pytest.Config,
) -> None:
    """Ensure that our plugin is loaded in the current pytest session.

    Due to some caching problems this was not the case for some environments in CI.
    """
    pytestconfig.pluginmanager.has_plugin(pytest_sigil._PYTEST_PLUGIN_NAME)


def test_plugin_registered_via_entry_point() -> None:
    """Verify the plugin is registered via entry point metadata."""
    entry_points = metadata.entry_points(group="pytest11")
    assert any(ep.name == pytest_sigil._PYTEST_PLUGIN_NAME for ep in entry_points), (
        f"Plugin '{pytest_sigil._PYTEST_PLUGIN_NAME}' not found in pytest11 entry points"
    )


@pytest.mark.parametrize(
    "plugin_enabled, expected_exit_code",
    [
        pytest.param(True, pytest.ExitCode.INTERRUPTED, id="plugin-enabled"),
        pytest.param(False, -15, id="plugin-disabled"),
    ],
)
def test_sigterm_handling_with(
    pytester: pytest.Pytester,
    plugin_enabled: bool,
    expected_exit_code: int,
) -> None:
    """Test how pytest handles SIGTERM with and without the plugin enabled."""
    stamp_file = pytester.path / "test_started.stamp"
    assert not stamp_file.exists()

    pytester.makepyfile(
        f"""
def test_wait_to_be_interrupted():
    import pathlib
    pathlib.Path("{stamp_file}").touch()
    import time
    time.sleep(5)
"""
    )
    command_args = [sys.executable, "-m", "pytest"]
    command_args += (
        ["-p", f"no:{pytest_sigil._PYTEST_PLUGIN_NAME}"] if not plugin_enabled else []
    )

    process = pytester.popen(command_args, text=True)

    while not stamp_file.exists():
        time.sleep(0.1)

    process.send_signal(signal.SIGTERM)
    process.wait(timeout=0.5)

    assert process.returncode == expected_exit_code, f"{process.stdout.read()=}"
