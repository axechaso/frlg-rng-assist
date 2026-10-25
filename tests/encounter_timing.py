"""Source-based script phase fixture, not a ROM or hardware execution.

References in pret/pokefirered at c75f352304d529f6ba92d4f74b9cf8b5c3810788:
src/main.c: AgbMain / VBlankIntr; src/link_rfu_2.c: RfuMain1;
src/script.c: RunScriptCommand; src/scrcmd.c: ScrCmd_lock;
src/event_object_lock.c: Task_WaitPlayerAndTargetNPCStopMoving;
data/maps/{SeafoamIslands_B4F,PowerPlant,MtEmber_Summit}/scripts.inc.

The native-script completion returns for that pass, even when it succeeds.
Birds first yield at lock, then at the successful native completion. Mewtwo
already waits in native mode, so yields only at its button-wait completion.
Assume stationary objects, no lag and no unrelated RNG draws. RFU draws once
before callbacks on each pass; VBlank draws once between passes. No production
encounter offsets are imported or used here.
"""


def generation_trace(seed, target, lcg):
    mode = "native" if target == "mewtwo" else "bytecode"
    trace = [("post_vblank", seed)]
    for frame in range(3):
        seed = lcg.step(seed)
        trace.append((f"{frame}:rfu", seed))
        if mode == "native":
            # RunScriptCommand sets BYTECODE on success, then returns TRUE.
            mode = "bytecode"
            trace.append((f"{frame}:native_complete_return", seed))
        elif frame == 0:
            # ScrCmd_lock returns TRUE; RunTasks finishes the stationary lock.
            mode = "native"
            trace.append(("0:lock_yield_task_complete", seed))
        else:
            trace.append((f"{frame}:setwildbattle", seed))
            return seed, trace
        seed = lcg.step(seed)
        trace.append((f"{frame + 1}:vblank", seed))
    raise AssertionError("script did not reach setwildbattle")
