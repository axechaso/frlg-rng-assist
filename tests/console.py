"""Synthetic GBA memory + real compiled guest. This is not a ROM/hardware test."""

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_ARM, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as a

from frlg_rng_assist_core.backend import backend, predict
from frlg_rng_assist_core.native import PROFILES, guest, install_plan, payloads
from pokeldn.frlg.rom.english_names import BRACKETED
from encounter_timing import generation_trace

# This upstream table is keyed by FRENCH addresses, not English addresses.
# Build the ROM fixture independently of the plugin's address being tested.
FRENCH_GETTER, ENGLISH_OFFSET = next(
    (address, offset) for address, (name, offset) in BRACKETED.items() if name == "GetGeneratedTrainerIdLower"
)
ROM_GETTERS = {
    code: FRENCH_GETTER + (ENGLISH_OFFSET if code.endswith("E") else 0)
    for code in ("BPRE", "BPGE", "BPRF", "BPGF")
}

STOP = 0x02030000
BUFFER = 0x0201C000
PARAM = 0x02030200
SEED16 = 0x02020000
SB2 = 0x02024584
STATES = ("initial", "seed", "index", "cursor", "next", "target", "shown",
          "call_original")
STATE_BYTES = ("status", "reason", "notice", "work_active")
# Pinned host address facts, independently of the config word under test.
MON_DATA = {"BPRE": 0x08043390, "BPGE": 0x08043390, "BPRF": 0x080432E4, "BPGF": 0x080432E4}


class Console:
    def __init__(
        self,
        code="BPRE",
        target="mewtwo",
        initial=0xB8C0,
        index=3500,
        criteria=None,
        first=20000,
        last=200000,
        install=True,
        offset=None,
        method=1,
        chamber="monean",
        location="other",
        species=0,
        capture=False,
        capture_offset=241,
        capture_offset_max=None,
    ):
        self.code, self.profile = code, PROFILES[code]
        self.plan = install_plan(
            "firered" if code.startswith("BPR") else "leafgreen",
            code,
            target,
            first=first,
            last=last,
            criteria=criteria,
            offset=offset,
            method=method,
            chamber=chamber,
            location=location,
            species=species,
            capture=capture,
            capture_offset=capture_offset,
            capture_offset_max=capture_offset_max,
        )
        self.manifest = guest(self.plan)
        self.uc = Uc(UC_ARCH_ARM, UC_MODE_ARM)
        for base, size in (
            (0x02000000, 0x40000),
            (0x03000000, 0x8000),
            (0x04000000, 0x1000),
            (0x05000000, 0x1000),
            (0x06000000, 0x20000),
            (0x07000000, 0x1000),
            (0x08000000, 0x1000000),
        ):
            self.uc.mem_map(base, size)
        self.write(0x080000AC, int.from_bytes(code.encode(), "little"))
        self.write(0x080000BC, 10, 1)
        getter = ROM_GETTERS[code]
        self.uc.mem_write(getter, bytes.fromhex("0148008870470000") + SEED16.to_bytes(4, "little"))
        self.write(SEED16, initial, 2)
        self.write(self.profile["sb2ptr"], SB2)
        self.write(SB2 + 10, 12345, 2)
        self.write(SB2 + 12, 2791, 2)
        self.write(self.profile["table"], self.profile["original"])
        self.uc.mem_write(self.profile["original"] & ~1, bytes.fromhex("7047"))
        self.uc.mem_write(self.profile["cb1"] & ~1, bytes.fromhex("7047"))
        self.uc.mem_write(self.profile["cb2"] & ~1, bytes.fromhex("7047"))
        self.uc.mem_write(MON_DATA[code], bytes.fromhex("7047"))
        self.uc.mem_write(0x0807C418, bytes.fromhex("7047"))
        self.uc.mem_write(self.profile["battle_cb2"] & ~1, bytes.fromhex("7047"))
        self.write(0x04000208, 1, 2)
        self.write(0x04000000, 0x1040, 2)
        self.lcg, _ = backend()
        self.write(self.profile["rng"], self.lcg.advance(initial, index))
        self.seed = initial
        self.presses = []
        self.inputs = []
        self.input_keys = []
        self.input_addresses = (self.profile["cb1"] & ~1, 0x0807C418, self.profile["battle_cb2"] & ~1)
        self.phases = []
        self.mon_reads = []
        self.writes = []
        self.instructions = 0
        self.record = True
        self.uc.hook_add(UC_HOOK_CODE, self._code)
        self.uc.hook_add(UC_HOOK_MEM_WRITE, self._write)
        self.set_overworld()
        self.set_ready()
        if install:
            for part in payloads(self.plan, code):
                assert self.load(part) == 0x524E4703
            self.writes.clear()

    def _code(self, uc, address, size, user):
        self.instructions += 1
        if address == self.profile["original"] & ~1:
            # VBlankIntr transfers gMain.oamBuffer before our overlay updates.
            uc.mem_write(0x07000000, bytes(uc.mem_read(self.profile["main"] + 0x38, 1024)))
            self.write(self.profile["rng"], self.lcg.step(self.read(self.profile["rng"])))
            self.phases.append(("vblank", self.read(self.profile["rng"])))
        if address == MON_DATA[self.code]:
            # Substitute the ROM accessor, not an entire ROM execution. Reproduce
            # its XOR, block selection and checksum side effect on the argument.
            at = uc.reg_read(a.UC_ARM_REG_R0)
            assert uc.reg_read(a.UC_ARM_REG_R1) == 66
            self.mon_reads.append(at)
            raw = bytes(uc.mem_read(at, 100))
            pid, otid = self.read(at), self.read(at + 4)
            words = [self.read(at + off) ^ pid ^ otid for off in range(32, 80, 4)]
            checksum = sum((word & 65535) + (word >> 16) for word in words) & 65535
            bad = bool(raw[19] & 1 or checksum != self.read(at + 28, 2))
            if bad:
                uc.mem_write(at + 19, bytes((raw[19] | 1,)))
            misc = (3, 2, 3, 2, 1, 1) * 3 + (0,) * 6
            uc.reg_write(a.UC_ARM_REG_R0, 0 if bad else words[misc[pid % 24] * 3 + 1] & 0x3FFFFFFF)
        if address not in self.input_addresses:
            return
        capture_phase = self.read(self.manifest["symbols"]["config"] + 78, 1) == 2
        trigger = 1 if capture_phase else self.plan["trigger_key_mask"]
        if self.read(self.profile["main"] + 0x2E, 2) & trigger:
            self.inputs.append((address, self.read(self.profile["rng"])))
            self.input_keys.append((self.read(self.profile["main"] + 0x2C, 2),
                                    self.read(self.profile["main"] + 0x2E, 2)))
            self.phases.append(("callback1_a", self.read(self.profile["rng"])))
            # Forecast script completion from explicit per-pass yields, not a
            # configured number of immediate generation draws. main_loop has
            # already applied the first RFU draw; the trace starts before it.
            if not capture_phase and self.plan["target"] in ("mewtwo", "articuno", "zapdos", "moltres"):
                post_vblank = self.lcg.advance(self.read(self.profile["rng"]), 0xFFFFFFFF)
                seed, _ = generation_trace(post_vblank, self.plan["target"], self.lcg)
                self.presses.append((seed, predict(seed, 12345, 2791)))

    def _write(self, uc, access, address, size, value, user):
        if self.record:
            self.writes.append((address, size, value))

    def read(self, at, size=4):
        return int.from_bytes(self.uc.mem_read(at, size), "little")

    def write(self, at, value, size=4):
        if at == self.profile["main"] + 0x2C and size == 2:
            self.physical_keys = value
        self.uc.mem_write(at, int(value).to_bytes(size, "little"))

    def s(self, name, value=None):
        base = self.manifest["symbols"]["state"]
        scratch = {"call_slot": 48, "call_context": 60, "work_cursor": 56}
        if name in scratch:
            at, size = self.manifest["symbols"]["config"] + scratch[name], 4
        else:
            at, size = ((base + STATE_BYTES.index(name), 1) if name in STATE_BYTES
                        else (base + 4 + STATES.index(name) * 4, 4))
        if value is not None:
            self.write(at, value, size)
        return self.read(at, size)

    def call(self, entry, *args):
        for register, value in zip((a.UC_ARM_REG_R0, a.UC_ARM_REG_R1, a.UC_ARM_REG_R2), args):
            self.uc.reg_write(register, value)
        self.uc.reg_write(a.UC_ARM_REG_SP, 0x03007D00)
        self.uc.reg_write(a.UC_ARM_REG_LR, STOP)
        self.uc.emu_start(entry, STOP, count=200000)
        assert self.uc.reg_read(a.UC_ARM_REG_PC) == STOP, "payload did not return"
        return self.uc.reg_read(a.UC_ARM_REG_R0)

    def load(self, blob):
        self.uc.mem_write(BUFFER, blob)
        self.call(BUFFER, PARAM, SB2, 0x02025500)
        return self.read(PARAM)

    def set_overworld(self, value=True):
        self.write(self.profile["main"], self.profile["cb1"] if value else 0)
        self.write(self.profile["main"] + 4, self.profile["cb2"] if value else 0x0807C419)

    def set_ready(self):
        from frlg_rng_assist_core.native import ENCOUNTERS

        target = self.profile["objects"] + 36
        self.write(target, 1)
        self.write(target + 5, ENCOUNTERS[self.plan["target"]].graphics, 1)
        self.write(target + 16, 14, 2)
        self.write(target + 18, 19, 2)
        self.write(target + 11, 3, 1)
        player = self.profile["objects"]
        self.write(player, 0x10001)
        self.write(player + 16, 14, 2)
        self.write(player + 18, 20, 2)
        self.write(player + 24, 2, 1)
        self.write(player + 11, 3, 1)
        self.write(self.profile["selected"], 1, 1)
        self.write(self.profile["context"] + 1, 2 if self.plan["profile"] == "mewtwo" else 0, 1)
        self.write(self.profile["context"] + 4, self.profile["wait"])
        self.write(self.profile["main"] + 0x2C, 0, 2)

    def frame(self, index=None, *, lag=False):
        if index is not None:
            self.write(self.profile["rng"], self.lcg.advance(self.seed, index - 1))
        self.write(self.profile["main"] + 0x1C, int(lag), 2)
        self.call(self.read(self.profile["table"]))

    def main_loop(self, *, rfu_calls=1):
        self.write(self.profile["main"] + 0x2C, self.physical_keys, 2)
        self.write(self.profile["main"] + 0x2E, 0, 2)  # ReadKeys
        # RfuMain1 passes Random() to rfu_LMAN_manager_entity before CallCallbacks,
        # including after the RFU manager shuts down. This was absent in <=0.3.6.
        for _ in range(rfu_calls):
            self.write(self.profile["rng"], self.lcg.step(self.read(self.profile["rng"])))
        self.phases.append(("link", self.read(self.profile["rng"])))
        cb1 = self.read(self.profile["main"])
        if cb1:
            self.call(cb1)
        cb2 = self.read(self.profile["main"] + 4)
        if cb2:
            self.call(cb2)
        return self.read(self.profile["main"] + 0x2E, 2)

    def resume_after_notice(self):
        assert self.s("status") == 4
        reason = self.s("reason")
        for _ in range(61):
            self.frame(self.s("index") + 2)
            if self.s("status") != 4:
                return
            assert self.s("shown") == 0xD0000000 + int(str(reason), 16)
            assert self.main_loop() == 0
        raise AssertionError("notice did not resume within 61 map frames")
