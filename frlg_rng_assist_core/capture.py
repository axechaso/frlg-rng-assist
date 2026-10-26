"""Conservative natural capture windows, matching the supplied v24 / v27g tools.

An offset counts from the A callback's seed to BEFORE the first shake's Random.
The console additionally accounts for its one RFU draw before that callback.
No HP, ball, status, encounter-generation offset or clock-rate inference is used.
"""

from .backend import backend, bounded

THRESHOLD = 16643
DEFAULT_OFFSET = 241
MAX_BAND_WIDTH = 12


def settings(enabled=False, first=DEFAULT_OFFSET, last=None):
    if type(enabled) is not bool:
        raise ValueError("捕获开关必须是布尔值")
    bounded(first, 0, 65532, "捕获 Offset 下限")
    last = first if last is None else bounded(last, first, 65532, "捕获 Offset 上限")
    if last - first > MAX_BAND_WIDTH:
        raise ValueError("捕获 Offset 上下限之差不能超过 12 advances")
    return {
        "enabled": enabled,
        "threshold": THRESHOLD,
        "offset_min": first,
        "offset_max": last,
        "offset_origin": "input_callback_seed_to_before_first_shake_random",
        "arming": "R+SELECT after generation input; press again to cancel",
        "search_end": 9999999,
        "model_source": "frlg_capture_engine_v24.check_capture_band / v27g.verify_band",
        "hardware_tested": False,
    }


def check_band(seed, first, last):
    """Every possible offset must pass all four STRICT shake comparisons."""
    plan = settings(True, first, last)
    lcg, _ = backend()
    cursor = lcg.advance(seed, first)
    for _ in range(plan["offset_max"] - first + 4):
        cursor = lcg.step(cursor)
        if cursor >> 16 >= THRESHOLD:
            return False
    return True


def find_window(seed, start, end, first=DEFAULT_OFFSET, last=None):
    """Inclusive offline reference scanner; the resident searches incrementally."""
    plan = settings(True, first, last)
    bounded(start, 0, 9999999, "范围起点")
    bounded(end, start, 9999999, "范围终点")
    lcg, _ = backend()
    cursor = lcg.advance(seed, start)
    for index in range(start, end + 1):
        if check_band(cursor, first, plan["offset_max"]):
            return index
        cursor = lcg.step(cursor)
    return None
