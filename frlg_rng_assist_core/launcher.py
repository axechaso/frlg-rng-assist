"""Run the built-in catalog tool in the existing managed child, including packaged Windows apps."""

import importlib.util
import os
from pathlib import Path
import re
import runpy
import sys


class HostFailure(RuntimeError):
    def __init__(self, code, statuses=()):
        self.code = code
        self.statuses = tuple(statuses)
        super().__init__(f"PokeLDN 会话结束，退出码 {code}；没有确认成功。")


class StatusOutput:
    """Forward the host log without keeping keys or trainer data; retain scalar evidence only."""

    def __init__(self, stream):
        self.stream = stream
        self.pending = ""
        self.statuses = []

    def __getattr__(self, name):
        return getattr(self.stream, name)

    def write(self, text):
        result = self.stream.write(text)
        self.pending += text
        while "\n" in self.pending:
            line, self.pending = self.pending.split("\n", 1)
            self.observe(line)
        self.pending = self.pending[-65536:]
        return result

    def observe(self, line):
        match = re.search(r"Buffer script status:\s*0x([0-9A-Fa-f]{8})\b", line)
        if match:
            self.statuses.append(int(match[1], 16))

    def flush(self):
        return self.stream.flush()


def gift_script():
    from pokeldn.app.catalog import GAMES

    tool = next(
        (tool for game in GAMES if game.key == "frlg" for tool in game.tools if tool.key == "frlg-gift"), None
    )
    if tool is None:
        raise RuntimeError("PokeLDN 的公开工具目录中没有 frlg-gift")
    path = Path(tool.script)
    if not path.is_absolute():
        spec = importlib.util.find_spec("pokeldn")
        roots = tuple(spec.submodule_search_locations or ()) if spec else ()
        if not roots:
            raise RuntimeError("找不到 PokeLDN 工具目录")
        path = Path(roots[0]).parent / path
    if not path.is_file():
        raise RuntimeError("找不到内置 Mystery Gift 启动脚本；请检查 PokeLDN 安装")
    return path.resolve()


def run_gift(arguments, *, radio=None):
    """The public catalog promises launcher scripts and stable flags (docs/plugins.md).

    run_path avoids starting another Python executable: the released app is a frozen executable,
    and the current tool process already owns Stop, popups and the app's stdin.
    """
    script = gift_script()
    previous_argv, previous_path = sys.argv, list(sys.path)
    previous_stdout = sys.stdout
    output = StatusOutput(previous_stdout)
    previous_radio = os.environ.get("POKELDN_RADIO")
    failure = None
    try:
        if radio:
            os.environ["POKELDN_RADIO"] = radio
        sys.stdout = output
        sys.argv = [str(script), *map(str, arguments)]
        try:
            runpy.run_path(str(script), run_name="__main__")
        except SystemExit as exc:
            code = 0 if exc.code is None else exc.code
            if code != 0:
                failure = code if type(code) is int else 1
    finally:
        output.observe(output.pending)
        sys.stdout = previous_stdout
        sys.argv = previous_argv
        sys.path[:] = previous_path
        if previous_radio is None:
            os.environ.pop("POKELDN_RADIO", None)
        else:
            os.environ["POKELDN_RADIO"] = previous_radio
    if failure is not None:
        raise HostFailure(failure, output.statuses)
    return output.statuses
