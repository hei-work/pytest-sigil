"""pytest_sigil - Proper fixture resource cleanup by handling signals."""

__version__ = "1.0.0"

import pathlib

_PACKAGE_ROOT_DIRECTORY = pathlib.Path(__file__).resolve().parent
"""The root directory of the installed package."""

_DISTRIBUTION_PACKAGE_NAME = "PYTEST_SIGIL"
"""Distribution name of this package, upper case & underscore separators.

.. note:: Use this as prefix when defining environment variables for this package.
"""

_PYTEST_PLUGIN_NAME = "sigil"
"""Name of the pytest plugin provided by this package."""
