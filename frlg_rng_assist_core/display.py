"""The public progress and status-card APIs; no UI work when importing a tool."""

from .backend import NATURES_ZH


def progress(done, total):
    from pokeldn import progress as bar

    bar.show(done, total, "离线 RNG 候选", "items")


def card(title, lines, *, ok=None):
    from pokeldn import panel

    panel.show("rng-assist", title, lines, tone="info" if ok is None else "ok" if ok else "error")


def mon_line(mon):
    return (
        f"PID {mon['pid']:08X} | {'闪光' if mon['shiny'] else '非闪光'} | "
        f"{NATURES_ZH[mon['nature']]} | IV {'/'.join(map(str, mon['ivs']))}"
    )
