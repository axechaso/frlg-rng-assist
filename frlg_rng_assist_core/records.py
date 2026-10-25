"""Append-only reports in the public plugin library."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from uuid import uuid4

from . import PLUGIN_ID, VERSION


def report_path(output, kind):
    if output:
        path = Path(output).expanduser().resolve()
    else:
        from pokeldn.plugins import library_folder

        try:
            folder = library_folder(PLUGIN_ID)
        except LookupError:
            raise ValueError("请通过插件运行，或使用 --output 指定新报告路径") from None
        stem = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid4().hex[:6]
        path = folder / f"{stem}-{kind}.json"
    if path.exists():
        raise FileExistsError(f"报告已存在：{path}；请选择新文件名")
    if not path.parent.is_dir():
        raise ValueError("报告的上级目录不存在")
    return path


def save_report(report, path):
    report = {
        "schema": 2,
        "plugin_version": VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        **report,
    }
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return path


def capture_path(report, suffix):
    path = Path(report).with_suffix(suffix)
    if path.exists():
        raise FileExistsError(f"采集文件已存在：{path}")
    return path


def read_capture(path, size):
    with Path(path).open("rb") as stream:
        data = stream.read(size + 1)
    if len(data) != size:
        raise ValueError(f"采集应为 {size} 字节，实际 {len(data)} 字节")
    return data


def digest(data):
    return hashlib.sha256(data).hexdigest()


def installation(path, game, build, target):
    if not path:
        return None
    with Path(path).open(encoding="utf-8") as stream:
        text = stream.read(65537)
    if len(text) > 65536:
        raise ValueError("安装报告过大")
    data = json.loads(text)
    if (
        not isinstance(data, dict)
        or data.get("schema") != 2
        or data.get("kind") != "native_install"
        or data.get("status") != "installed"
    ):
        raise ValueError("请选择收到安装回执的 0.3.0 或更新版本安装报告")
    if data.get("game") != game or data.get("target") != target:
        raise ValueError("安装报告的游戏或目标与本次核对不一致")
    if build != "auto" and data.get("build") not in ("auto", build):
        raise ValueError("安装报告的卡带构建与本次核对不一致")
    from .model import Criteria
    from .native import ACK

    if data.get("installer_ack") != ACK:
        raise ValueError("安装报告没有本版掌机端的完整传输回执")
    try:
        Criteria(**data["criteria"])
        first, last = data["range"]["first"], data["range"]["last"]
        if not (type(first) is int and type(last) is int and 0 <= first <= last <= 9999999):
            raise ValueError()
    except (KeyError, TypeError, ValueError):
        raise ValueError("安装报告的筛选条件或搜索范围无效") from None
    return {
        "path": str(Path(path).resolve()),
        "sha256": digest(text.encode("utf-8")),
        "criteria": data["criteria"],
        "range": data["range"],
    }
