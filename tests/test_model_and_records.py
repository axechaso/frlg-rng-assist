import json
import struct

import pytest

from frlg_rng_assist_core.arguments import hex_word, ivs, nature
from frlg_rng_assist_core.backend import backend, predict, recover
from frlg_rng_assist_core.model import Criteria, recovery_report, search
from frlg_rng_assist_core.native import ACK, install_plan, validate_install_ack, write_gift
from frlg_rng_assist_core.pk3 import ORDERS, choose_record, decode_mon, party_records
from frlg_rng_assist_core.records import installation, read_capture, save_report
from frlg_rng_assist_core.verification import verify


def record(
    pid=0x12345678,
    *,
    encrypted=False,
    species=150,
    values=(31, 1, 22, 13, 4, 25),
    tid=12345,
    sid=2791,
    origin=4,
):
    raw, secure = bytearray(100), bytearray(48)
    struct.pack_into("<II", raw, 0, pid, tid | sid << 16)
    raw[19] = 2
    struct.pack_into("<H", secure, 0, species)
    # Distinct contents exercise the permutation of all four blocks.
    secure[12:24] = b"ABCDEFGHIJKL"
    secure[24:36] = b"mnopqrstuvwx"
    hp, attack, defense, spa, spd, speed = values
    word = sum(v << (i * 5) for i, v in enumerate((hp, attack, defense, speed, spa, spd)))
    struct.pack_into("<H", secure, 38, 70 | origin << 7)
    struct.pack_into("<I", secure, 40, word)
    struct.pack_into("<H", raw, 28, sum(struct.unpack("<24H", secure)) & 0xFFFF)
    if encrypted:
        blocks = {letter: secure[i * 12 : i * 12 + 12] for i, letter in enumerate("GAEM")}
        secure = b"".join(blocks[letter] for letter in ORDERS[pid % 24])
        key = pid ^ (tid | sid << 16)
        secure = b"".join((v ^ key).to_bytes(4, "little") for v in struct.unpack("<12I", secure))
    raw[32:80] = secure
    raw[84] = 70
    return bytes(raw)


@pytest.mark.parametrize("order", range(24))
def test_all_encrypted_orders_and_canonical_exports_agree(order):
    a = decode_mon(record(order), encrypted=False)
    b = decode_mon(record(order, encrypted=True), encrypted=True)
    assert a == b
    assert a["ivs"] == (31, 1, 22, 13, 4, 25)


def test_party_count_is_byte_and_ambiguous_species_requires_explicit_slot():
    raw = bytes((2, 255, 255, 255)) + record(encrypted=True) * 2 + bytes(404)
    records = party_records(raw)
    assert len(records) == 2
    with pytest.raises(ValueError, match="多个"):
        choose_record(records, 150)
    assert choose_record(records, 150, 2)["slot"] == 2
    with pytest.raises(ValueError, match="为空"):
        choose_record(records, 150, 3)


def test_bad_checksum_and_bad_egg_are_refused():
    broken = bytearray(record())
    broken[32] ^= 1
    with pytest.raises(ValueError, match="校验和"):
        decode_mon(broken, encrypted=False)
    broken = bytearray(record())
    broken[19] |= 1
    with pytest.raises(ValueError, match="Bad Egg"):
        decode_mon(broken, encrypted=False)


@pytest.mark.parametrize("method", [1, 2, 4])
def test_public_prediction_recovery_round_trip(method):
    seed = 0x12345678
    mon = predict(seed, 12345, 2791, method)
    assert {"generation_seed": seed, "method": method} in recover(mon["personality"], mon["ivs"])
    assert recovery_report(mon["personality"], mon["ivs"], reference_seed=seed, max_offset=0)["candidates"]


def test_offline_search_is_bounded_and_not_live():
    lcg, _ = backend()
    start = 17
    seed = 0x12345678
    mon = predict(lcg.advance(seed, start), 12345, 2791)
    report = search(
        seed,
        12345,
        2791,
        start=start,
        advances=1,
        criteria=Criteria(False, mon["nature"], mon["personality"], mon["ivs"], mon["ivs"]),
    )
    assert len(report["targets"]) == 1
    assert report["targets"][0]["advance"] == start
    assert report["candidates_tested"] == 1
    assert not report["live_synchronized"]
    assert not report["can_schedule_inputs"]
    with pytest.raises(ValueError):
        search(seed, 12345, 2791, start=0xFFFFFFFF, advances=2)


def test_capture_verification_checks_range_and_reports_its_actual_scope():
    lcg, _ = backend()
    initial, advance = 0xB8C0, 20000
    seed = lcg.advance(initial, advance)
    prediction = predict(seed, 12345, 2791)
    mon = decode_mon(record(prediction["personality"], values=prediction["ivs"]), encrypted=False)
    report = verify(
        mon,
        "firered",
        "mewtwo",
        shiny=False,
        initial_seed=initial,
        search_range={"first": advance, "last": advance},
    )
    assert report["status"] == "matched"
    assert report["range_verified"]
    assert not report["input_timing_measured"]
    assert report["evidence_scope"] == "selected_pokemon_record"
    wrong = verify(
        mon,
        "firered",
        "mewtwo",
        shiny=False,
        initial_seed=initial,
        search_range={"first": advance + 1, "last": advance + 2},
    )
    assert wrong["status"] == "mismatch"
    assert not wrong["checks"]["advance_range"]


def test_report_writes_never_overwrite_and_association_requires_final_ack(tmp_path):
    path = tmp_path / "install.json"
    plan = install_plan("firered", "auto", "mewtwo")
    plan.update(status="installed", installer_ack=ACK)
    save_report(plan, path)
    assert installation(path, "firered", "auto", "mewtwo")["range"]["first"] == 10000
    with pytest.raises(FileExistsError):
        save_report(plan, path)
    with pytest.raises(ValueError):
        installation(path, "firered", "auto", "zapdos")
    data = json.loads(path.read_text(encoding="utf-8"))
    data["installer_ack"] = 0x08000735
    other = tmp_path / "old.json"
    other.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="回执"):
        installation(other, "firered", "auto", "mewtwo")
    with pytest.raises(ValueError):
        read_capture(path, 608)


@pytest.mark.parametrize("statuses", [[], [0xBAD00001], [ACK, ACK], [0x08000735], [0]])
def test_missing_wrong_or_duplicate_install_ack_never_succeeds(statuses):
    with pytest.raises(ValueError):
        validate_install_ack(statuses)


def test_public_gift_file_loader_checks_export_and_builds(tmp_path):
    from pokeldn.gifts import load

    path = tmp_path / "test.pokegift"
    info = write_gift(install_plan("leafgreen", "auto", "moltres"), path)
    gift = load(path, game="frlg")
    assert set(gift.variants) == {"BPGE", "BPGF"}
    assert info["resident_bytes"] > 1024
    assert all(variant.options["buffer_expect"] == ACK for variant in gift.variants.values())
    assert all(len(blob) <= 1024 for variant in gift.variants.values() for blob in variant.data.values())


def test_input_formats_and_invalid_criteria():
    assert hex_word("0xB8C0") == 0xB8C0
    assert ivs("31/0/31/31/31/31") == (31, 0, 31, 31, 31, 31)
    assert nature("胆小") == nature("Timid") == 10
    for kwargs in ({"iv_min": (32,) * 6}, {"iv_min": (31,) * 6, "iv_max": (0,) * 6}, {"nature": 25}):
        with pytest.raises(ValueError):
            Criteria(**kwargs)
    with pytest.raises(ValueError):
        install_plan("firered", "BPRJ", "mewtwo")
    with pytest.raises(ValueError):
        install_plan("firered", "BPGE", "mewtwo")
