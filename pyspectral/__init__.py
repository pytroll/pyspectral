"""Pyspectral package init."""

try:
    from pyspectral.version import version as __version__  # noqa
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "No module named pyspectral.version. This could mean "
        "you didn't install 'pyspectral' properly. Try reinstalling ('pip "
        "install pyspectral').")
