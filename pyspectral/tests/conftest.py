"""Shared test preparation and utilities."""

import pytest

from pyspectral.testing import forbid_pyspectral_downloads


@pytest.fixture(autouse=True, scope="session")
def _forbid_pyspectral_downloads():
    """Raise an error if LUT downloads are attempted.

    See the used context manager for more information.

    """
    with forbid_pyspectral_downloads():
        yield
