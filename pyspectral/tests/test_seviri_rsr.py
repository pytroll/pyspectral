"""Regression tests for the SEVIRI RSR converter.

Ensures the first spreadsheet row of each IR channel is included when
converting the bundled MSG SEVIRI spectral response workbook (issue #253).
"""

import importlib
import sys
import types
from pathlib import Path

from xlrd import open_workbook


def _import_seviri_module(repo_root: Path):
    sys.modules.pop("rsr_convert_scripts.seviri_rsr", None)
    sys.modules["pkg_resources"] = types.SimpleNamespace(
        resource_filename=lambda package, resource: str(repo_root / "pyspectral" / "data")
    )
    return importlib.import_module("rsr_convert_scripts.seviri_rsr")


def test_ir_channels_include_the_first_spreadsheet_row(monkeypatch):
    """IR channel RSR data must start at spreadsheet row 12, not row 13."""
    repo_root = Path(__file__).resolve().parents[2]
    xls_path = repo_root / "pyspectral" / "data" / "MSG_SEVIRI_Spectral_Response_Characterisation.XLS"
    workbook = open_workbook(str(xls_path))
    sheet = workbook.sheet_by_name("IR7.3")

    # The issue's concrete repro: the first wavelength/data row is line 13 in the
    # spreadsheet UI, which is row index 12 for xlrd.
    assert sheet.cell_value(12, 0) == 6.35
    assert sheet.cell_value(13, 0) == 6.37

    seviri_rsr = _import_seviri_module(repo_root)
    monkeypatch.setattr(
        seviri_rsr,
        "get_config",
        lambda: {
            "seviri": {"path": str(xls_path), "filename": xls_path.name},
            "rsr_dir": str(repo_root / "tmp-rsr"),
        },
    )

    seviri = seviri_rsr.Seviri()

    assert seviri.rsr["IR7.3"]["wavelength"][0] == sheet.cell_value(12, 0)
    assert seviri.rsr["IR7.3"]["Meteosat-11"]["95"][0] == sheet.cell_value(12, 7)
