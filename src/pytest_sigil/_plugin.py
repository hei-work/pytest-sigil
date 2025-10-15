import signal

import pytest

_SIGTERM_SIGNAL_HANDLER = pytest.StashKey[signal.Handlers]()


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session: pytest.Session) -> None:
    """Reroute SIGTERM → SIGINT early in the pytest lifecycle."""
    session.stash[_SIGTERM_SIGNAL_HANDLER] = signal.signal(  # type: ignore[misc]  # signal type hints (typeshed) are lacking
        signal.SIGTERM, signal.getsignal(signal.SIGINT)
    )


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session: pytest.Session) -> None:
    """Restore SIGTERM handler after pytest completes."""
    original = session.stash[_SIGTERM_SIGNAL_HANDLER]
    signal.signal(signal.SIGTERM, original)
