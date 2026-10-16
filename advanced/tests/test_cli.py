import pytest

from kp.cli import main


def test_init_command_reports_nothing_to_create(project, capsys):
    assert main(["init"]) == 0
    assert "nothing to create" in capsys.readouterr().out


def test_version_flag(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert "kp 2.0.0" in capsys.readouterr().out
