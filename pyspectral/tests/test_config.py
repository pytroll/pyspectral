"""Tests for the configuration handling."""

import pytest

from pyspectral.config import get_config


@pytest.mark.parametrize("dir_key", ["rsr_dir", "rayleigh_dir"])
def test_get_config_tolerates_dangling_symlink(tmp_path, dir_key):
    """``get_config`` must not crash on a configured directory behind a dangling symlink.

    ``os.makedirs(..., exist_ok=True)`` raises ``FileExistsError`` in that
    case; the target directory should be created instead.
    """
    target = tmp_path / "real"
    link = tmp_path / "data"
    link.symlink_to(target, target_is_directory=True)

    other = tmp_path / "other"
    settings = {"rsr_dir": other, "rayleigh_dir": other}
    settings[dir_key] = link
    cfg_file = tmp_path / "cfg.yaml"
    cfg_file.write_text("".join(f"{key}: {value}\n" for key, value in settings.items()))

    get_config(str(cfg_file))

    assert target.is_dir()
    assert other.is_dir()


def test_get_config_creates_missing_directories(tmp_path):
    """Ordinary missing directories are created as before."""
    data = tmp_path / "data"
    cfg_file = tmp_path / "cfg.yaml"
    cfg_file.write_text(f"rsr_dir: {data}\nrayleigh_dir: {data}\n")

    get_config(str(cfg_file))

    assert data.is_dir()
