"""Tests for vigor.compose module."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from vigor.compose import Compose


@pytest.fixture
def compose() -> Compose:
    return Compose("test-project")


def test_compose_init(compose: Compose) -> None:
    assert compose.project_name == "test-project"


def test_generate_compose_file_relative_path_raises(compose: Compose) -> None:
    with pytest.raises(ValueError, match="must be an Absolute Path"):
        compose.generate_compose_file(["relative/docker-compose.yml"])


def test_generate_compose_file_relative_env_raises(
    compose: Compose, temp_dir: Path
) -> None:
    compose_file = temp_dir / "docker-compose.yml"
    compose_file.write_text("version: '3'\nservices: {}")

    with pytest.raises(ValueError, match="must be an Absolute Path"):
        compose.generate_compose_file([str(compose_file)], env="relative/.env")


def test_generate_compose_file(
    compose: Compose, temp_dir: Path, mocker: MagicMock
) -> None:
    compose_file = temp_dir / "docker-compose.yml"
    compose_file.write_text("version: '3'\nservices:\n  web:\n    image: nginx")

    mock_result = MagicMock()
    mock_result.stdout = "name: test-project\nservices:\n  web:\n    image: nginx\n"
    mocker.patch.object(compose, "run", return_value=mock_result)

    result = compose.generate_compose_file([str(compose_file)])

    assert "nginx" in result
    compose.run.assert_called_once()


def test_generate_compose_file_with_env(
    compose: Compose, temp_dir: Path, mocker: MagicMock
) -> None:
    compose_file = temp_dir / "docker-compose.yml"
    compose_file.write_text("version: '3'\nservices:\n  web:\n    image: nginx")
    env_file = temp_dir / ".env"
    env_file.write_text("FOO=bar")

    mock_result = MagicMock()
    mock_result.stdout = "parsed config"
    mocker.patch.object(compose, "run", return_value=mock_result)

    result = compose.generate_compose_file([str(compose_file)], env=str(env_file))

    assert result == "parsed config"
    call_args = compose.run.call_args[0]
    assert "--env-file" in call_args
    assert str(env_file) in call_args


def test_run_builds_correct_command(compose: Compose, mocker: MagicMock) -> None:
    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)

    compose.run("up", "-d")

    mock_run.assert_called_once()
    call_args = mock_run.call_args[0][0]
    assert list(call_args[:4]) == ["docker", "compose", "-p", "test-project"]
    assert "up" in call_args
    assert "-d" in call_args
