"""Exercise tool entry points and host failures, beyond the guest's memory model."""

import io
import json
import os
import sys

import pytest

import install
import verify as verify_tool
from frlg_rng_assist_core import launcher
from frlg_rng_assist_core.backend import backend, predict
from frlg_rng_assist_core.native import ACK, install_plan
from frlg_rng_assist_core.records import save_report
from test_model_and_records import record


def test_preview_exports_a_real_gift_without_starting_a_host(tmp_path, monkeypatch, capsys):
    def unexpected(*args, **kwargs):
        pytest.fail("preview started the radio host")

    monkeypatch.setattr(install, "run_gift", unexpected)
    output = tmp_path / "预览配置.json"
    assert install.main(["--preview", "--allow-normal", "--output", str(output), "--json"]) == 0
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["status"] == "preview"
    assert data["criteria"]["shiny"] is False
    assert not data["hardware_tested"]
    assert output.with_suffix(".pokegift").is_file()
    assert json.loads(capsys.readouterr().out)["range"]["origin"] == "title_reseed_initial_seed"


@pytest.mark.parametrize("statuses", [[], [0xBAD00005], [ACK, ACK]])
def test_failed_ack_does_not_create_an_installed_report(tmp_path, monkeypatch, statuses):
    monkeypatch.setattr(install, "run_gift", lambda *a, **k: statuses)
    output = tmp_path / "failed.json"
    with pytest.raises(SystemExit) as error:
        install.main(["--enable-auto-a", "--output", str(output), "--json"])
    assert error.value.code == 2
    assert not output.exists()


def test_host_failure_is_propagated_without_a_success_report(tmp_path, monkeypatch):
    def failure(*args, **kwargs):
        raise launcher.HostFailure(124)

    monkeypatch.setattr(install, "run_gift", failure)
    output = tmp_path / "timeout.json"
    assert install.main(["--enable-auto-a", "--output", str(output)]) == 124
    assert not output.exists()


@pytest.mark.parametrize("status,reason", [(0xBAD00004, "初始 seed"), (0xBAD00005, "分段传输")])
def test_failed_host_preserves_and_explains_the_console_refusal(
    tmp_path, monkeypatch, capsys, status, reason
):
    def failure(*args, **kwargs):
        raise launcher.HostFailure(1, [status])

    monkeypatch.setattr(install, "run_gift", failure)
    output = tmp_path / "refused.json"
    assert install.main(["--enable-auto-a", "--output", str(output)]) == 1
    assert reason in capsys.readouterr().out
    assert not output.exists()


def test_capture_workflow_inherits_the_installation_and_checks_actual_advances(tmp_path, monkeypatch, capsys):
    lcg, _ = backend()
    initial, advance = 0xB8C0, 20000
    mon = predict(lcg.advance(initial, advance), 12345, 2791)
    monkeypatch.setattr(install, "run_gift", lambda *a, **k: [ACK])
    receipt = tmp_path / "installed.json"
    assert (
        install.main(
            [
                "--enable-auto-a",
                "--allow-normal",
                "--start",
                str(advance),
                "--end",
                str(advance + 10),
                "--output",
                str(receipt),
                "--json",
            ]
        )
        == 0
    )
    capsys.readouterr()
    pokemon = tmp_path / "Mewtwo.pk3"
    pokemon.write_bytes(record(mon["personality"], values=mon["ivs"]))
    result = tmp_path / "verified.json"
    assert (
        verify_tool.main(
            [
                "--pokemon",
                str(pokemon),
                "--installation",
                str(receipt),
                "--initial-seed",
                "B8C0",
                "--output",
                str(result),
                "--json",
            ]
        )
        == 0
    )
    data = json.loads(result.read_text(encoding="utf-8"))
    assert data["criteria"]["shiny"] is False
    assert data["range_verified"] is True
    assert not data["input_timing_measured"]
    # A different range must produce a failed check and a nonzero tool exit.
    wrong = tmp_path / "different-install.json"
    plan = install_plan("firered", "auto", "mewtwo", first=advance + 1, last=advance + 10)
    plan["criteria"]["shiny"] = False
    plan.update(status="installed", installer_ack=ACK)
    save_report(plan, wrong)
    assert (
        verify_tool.main(
            [
                "--pokemon",
                str(pokemon),
                "--installation",
                str(wrong),
                "--initial-seed",
                "B8C0",
                "--output",
                str(tmp_path / "mismatch.json"),
                "--json",
            ]
        )
        == 1
    )


@pytest.mark.parametrize("exit_code", [0, None, 124, "host error"])
def test_catalog_launcher_restores_process_state_even_when_host_exits(tmp_path, monkeypatch, exit_code):
    original_argv, original_path = sys.argv, list(sys.path)
    output = io.StringIO()
    monkeypatch.setattr(sys, "stdout", output)
    monkeypatch.setenv("POKELDN_RADIO", "original-radio")
    script = tmp_path / "host.py"
    monkeypatch.setattr(launcher, "gift_script", lambda: script)

    def host(path, *, run_name):
        assert path == str(script) and run_name == "__main__"
        assert sys.argv[1:] == ["--gift-file", "gift.pokegift"]
        assert os.environ["POKELDN_RADIO"] == "test-radio"
        sys.path.insert(0, "temporary-host-path")
        # Split writes and a final line without a newline still retain one acknowledgement.
        sys.stdout.write("[host] Buffer script sta")
        sys.stdout.write("tus: 0x524E4703")
        raise SystemExit(exit_code)

    monkeypatch.setattr(launcher.runpy, "run_path", host)
    if exit_code in (0, None):
        assert launcher.run_gift(["--gift-file", "gift.pokegift"], radio="test-radio") == [ACK]
    else:
        with pytest.raises(launcher.HostFailure) as error:
            launcher.run_gift(["--gift-file", "gift.pokegift"], radio="test-radio")
        assert error.value.code == (exit_code if type(exit_code) is int else 1)
        assert error.value.statuses == (ACK,)
    assert sys.stdout is output
    assert sys.argv is original_argv and sys.path == original_path
    assert os.environ["POKELDN_RADIO"] == "original-radio"
