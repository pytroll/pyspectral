"""Shared test preparation and utilities."""

import pytest

from pyspectral.testing import forbid_pyspectral_downloads


@pytest.fixture(autouse=True)
def _forbid_pyspectral_downloads(request):
    """Raise an error if LUT downloads are attempted.

    To allow downloads for a particular test, add:

    .. code-block:: python

        @pytest.mark.allow_downloads(use=True)
        def test_my_test():
            ...

    See the used context manager for more information on the mocking.

    """
    allow_downloads = request.node.get_closest_marker("allow_downloads")
    if allow_downloads:
        yield
        return

    with forbid_pyspectral_downloads():
        yield
