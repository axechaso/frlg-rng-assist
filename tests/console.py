"""Synthetic GBA memory + real compiled guest. This is not a ROM/hardware test."""

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_ARM, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as a

from frlg_rng_assist_core.backend import backend, predict
from frlg_rng_assist_core.native import PROFILES, guest, install_plan, payloads
from pokeldn.frlg.rom.english_names import BRACKETED

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
STATES = (
    "initial", "seed", "index", "cursor", "next", "target", "generation", "shown", "status", "reason", "locked"
)


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
    ):
        self.code, self.profile, self.manifest = code, PROFILES[code], guest()
        self.plan = install_plan(
            "firered" if code.startswith("BPR") else "leafgreen",
            code,
            target,
            first=first,
            last=last,
            criteria=criteria,
        )
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
        self.write(0x04000208, 1, 2)
        self.write(0x04000000, 0x1040, 2)
        self.lcg, _ = backend()
        self.write(self.profile["rng"], self.lcg.advance(initial, index))
        self.seed = initial
        self.presses = []
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
            self.write(self.profile["rng"], self.lcg.step(self.read(self.profile["rng"])))
        if address == self.profile["cb1"] & ~1 and self.read(self.profile["main"] + 0x2E, 2) & 1:
            seed = self.lcg.advance(self.read(self.profile["rng"]), self.plan["auto_a_offset_advances"])
            self.presses.append((seed, predict(seed, 12345, 2791)))

    def _write(self, uc, access, address, size, value, user):
        if self.record:
            self.writes.append((address, size, value))

    def read(self, at, size=4):
        return int.from_bytes(self.uc.mem_read(at, size), "little")

    def write(self, at, value, size=4):
        self.uc.mem_write(at, int(value).to_bytes(size, "little"))

    def s(self, name, value=None):
        at = self.manifest["symbols"]["state"] + STATES.index(name) * 4
        if value is not None:
            self.write(at, value)
        return self.read(at)

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

    def main_loop(self):
        self.write(self.profile["main"] + 0x2E, 0, 2)  # ReadKeys
        self.call(self.read(self.profile["main"]))
        return self.read(self.profile["main"] + 0x2E, 2)
