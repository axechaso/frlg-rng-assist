"""Build the standalone GBA payload. Requires GNU Arm Embedded; players need no compiler."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "frlg_rng_assist_core" / "guest.json"


def tool(name):
    prefix = os.environ.get("ARM_TOOLCHAIN", "")
    result = shutil.which(prefix + "arm-none-eabi-" + name)
    if not result:
        raise RuntimeError(f"找不到 arm-none-eabi-{name}；设置 ARM_TOOLCHAIN 为工具目录前缀")
    return result


def build_image(capture=False, model=-1):
    sources = [ROOT / "guest" / name for name in ("runtime.c", "runtime.ld")]
    with tempfile.TemporaryDirectory(prefix="frlg-rng-guest-") as folder:
        elf, binary = Path(folder) / "guest.elf", Path(folder) / "guest.bin"
        subprocess.run(
            [
                tool("gcc"),
                "-mthumb",
                "-mcpu=arm7tdmi",
                "-mthumb-interwork",
                "-Oz",
                "-fno-inline",
                "-fno-move-loop-invariants",
                "-fno-builtin",
                "-ffreestanding",
                "-fomit-frame-pointer",
                "-fno-unwind-tables",
                "-fno-asynchronous-unwind-tables",
                "-fno-common",
                "-nostdlib",
                *(["-fno-tree-ch"] if capture else []),
                *(["-fno-if-conversion", "-fno-tree-vrp", "-fno-tree-loop-im"]
                  if capture and model == 1 else []),
                *(["-fno-toplevel-reorder", "-fno-tree-pre", "-fno-ssa-phiopt",
                   "-fno-tree-vrp", "-fno-tree-loop-vectorize", "-fno-tree-dce", "-fno-tree-fre",
                   "-fno-if-conversion"]
                  if capture and model == 2 else []),
                f"-DWITH_CAPTURE={int(capture)}",
                f"-DGUEST_MODEL={model}",
                "-Wl,--build-id=none",
                "-T",
                str(sources[1]),
                str(sources[0]),
                "-lgcc",
                "-o",
                str(elf),
            ],
            check=True,
        )
        subprocess.run([tool("objcopy"), "-O", "binary", str(elf), str(binary)], check=True)
        listing = subprocess.check_output([tool("nm"), "-n", str(elf)], text=True)
        symbols = {
            parts[2]: int(parts[0], 16)
            for line in listing.splitlines()
            if len(parts := line.split()) == 3 and parts[1].upper() != "U"
        }
        code = binary.read_bytes()
    result = {
        "base": 0x0203F768,
        "hex": code.hex(),
        "length": len(code),
        "sha256": hashlib.sha256(code).hexdigest(),
        "source_sha256": hashlib.sha256(b"".join(path.read_bytes() for path in sources)).hexdigest(),
        "symbols": {
            name: symbols[name]
            for name in (
                "hook",
                "config",
                "state",
                "distance",
                "matches",
                "readiness",
                "press_shim",
                "tiles",
                "end",
            )
        },
    }
    return result


def build():
    result = build_image()
    result["capture_variants"] = {
        model: build_image(True, index) for index, model in enumerate(("static", "wild", "unown"))
    }
    with tempfile.TemporaryDirectory(prefix="frlg-rng-loader-") as folder:
        obj, binary = Path(folder) / "loader.o", Path(folder) / "loader.bin"
        source = ROOT / "guest" / "loader.s"
        subprocess.run([tool("as"), "-mcpu=arm7tdmi", str(source), "-o", str(obj)], check=True)
        subprocess.run([tool("objcopy"), "-O", "binary", "-j", ".text", str(obj), str(binary)], check=True)
        listing = subprocess.check_output([tool("nm"), "-n", str(obj)], text=True)
        symbols = {
            parts[2]: int(parts[0], 16)
            for line in listing.splitlines()
            if len(parts := line.split()) == 3 and parts[2].startswith("p_")
        }
        result["loader"] = {
            "hex": binary.read_bytes().hex(),
            "symbols": symbols,
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    rendered = json.dumps(result, indent=2) + "\n"
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("guest.json 与源文件不符；运行 scripts/build_guest.py")
    else:
        OUT.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"GBA resident: {result['length']} bytes, capacity {0x02040000 - result['base']} bytes")
    for model, variant in result["capture_variants"].items():
        print(f"GBA capture / {model}: {variant['length']} bytes")


if __name__ == "__main__":
    main()
