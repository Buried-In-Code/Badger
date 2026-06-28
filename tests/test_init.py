from pathlib import Path

from badger import get_cache_root, get_config_root, get_data_root, get_state_root


def test_get_cache_root_non_windows(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr("platform.system", lambda: "Linux")
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    result = get_cache_root()
    assert isinstance(result, Path)
    assert result.name == "badger"
    assert str(result).endswith("/.cache/badger")


def test_get_cache_root_custom_xdg(monkeypatch, tmp_path: Path) -> None:  # noqa: ANN001
    monkeypatch.setattr("platform.system", lambda: "Linux")
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    result = get_cache_root()
    assert result == tmp_path / "cache" / "badger"
    assert result.exists()


def test_get_cache_root_windows(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr("platform.system", lambda: "Windows")
    result = get_cache_root()
    assert result.name == ".badger"


def test_get_config_root_non_windows(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr("platform.system", lambda: "Linux")
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    result = get_config_root()
    assert result.name == "badger"
    assert str(result).endswith("/.config/badger")


def test_get_config_root_custom_xdg(monkeypatch, tmp_path: Path) -> None:  # noqa: ANN001
    monkeypatch.setattr("platform.system", lambda: "Linux")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    result = get_config_root()
    assert result == tmp_path / "config" / "badger"
    assert result.exists()


def test_get_config_root_windows(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr("platform.system", lambda: "Windows")
    result = get_config_root()
    assert result.name == ".badger"


def test_get_data_root_non_windows(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr("platform.system", lambda: "Linux")
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    result = get_data_root()
    assert result.name == "badger"
    assert str(result).endswith("/.local/data/badger")


def test_get_data_root_custom_xdg(monkeypatch, tmp_path: Path) -> None:  # noqa: ANN001
    monkeypatch.setattr("platform.system", lambda: "Linux")
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
    result = get_data_root()
    assert result == tmp_path / "data" / "badger"
    assert result.exists()


def test_get_data_root_windows(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr("platform.system", lambda: "Windows")
    result = get_data_root()
    assert result.name == ".badger"


def test_get_state_root_non_windows(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr("platform.system", lambda: "Linux")
    monkeypatch.delenv("XDG_STATE_HOME", raising=False)
    result = get_state_root()
    assert result.name == "badger"
    assert str(result).endswith("/.local/state/badger")


def test_get_state_root_custom_xdg(monkeypatch, tmp_path: Path) -> None:  # noqa: ANN001
    monkeypatch.setattr("platform.system", lambda: "Linux")
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    result = get_state_root()
    assert result == tmp_path / "state" / "badger"
    assert result.exists()


def test_get_state_root_windows(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr("platform.system", lambda: "Windows")
    result = get_state_root()
    assert result.name == ".badger"
