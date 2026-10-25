/* SPDX-License-Identifier: AGPL-3.0-or-later
 * Natural static / Method-H search. No stores to RNG, Pokemon, saves or ROM.
 * Addresses are injected for the four supported revision-0A builds.
 */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef void (*callback)(void);
#define U32(a) (*(volatile u32 *)(a))
#define U16(a) (*(volatile u16 *)(a))
#define U8(a) (*(volatile u8 *)(a))

struct Config {
    u32 main, rng, sb2ptr, cb1, cb2, original, seed_getter, palette, party, party_count, battle_cb2;
    u32 first, last, jump_a, jump_c, offset_a, offset_c;
    u16 offset;
    u8 model, method, shiny, nature, menus, button, minimum[6], maximum[6], letters[12];
};
__attribute__((section(".config"), used)) volatile struct Config config = {0};
enum { WAIT, SEARCH, FOUND, EXHAUSTED, MISSED, DESYNC, PENDING, FIRED };
/* Keep existing timing / Mewtwo reason numbers; retired bird gates have no code. */
enum { SCRIPT = 3, NOT_OVERWORLD, NO_TARGET, PASSED = 9, LAG, RNG_CHANGED, EXPIRED };
struct State { u32 initial, seed, index, cursor, next, target, generation, shown, status, reason, locked, notice;
    u32 call_slot, call_original, call_context, work_cursor, work_nature, work_active; };
__attribute__((section(".state"), used)) volatile struct State state = {0};
#define C config
#define S state

static u32 step(u32 v) { return v * 0x41C64E6D + 0x6073; }

static void miss(u32 reason) {
    S.reason = reason; S.notice = 60; S.status = MISSED;
}

/* Exact distance for this full-period LCG, one binary bit per iteration. */
__attribute__((noinline)) u32 distance(u32 from, u32 to) {
    u32 a = 0x41C64E6D, c = 0x6073, bit = 1, result = 0;
    do {
        if ((from ^ to) & bit) { from = from * a + c; result |= bit; }
        c *= a + 1;
        a *= a;
        bit <<= 1;
    } while (from != to && bit);
    return result;
}

static int overworld(void) { return U32(C.main) == C.cb1 && U32(C.main + 4) == C.cb2; }

/* The player chooses the final decision point. No object / held-key gates.
 * Menu tools wrap callback2, because a party menu has no overworld callback1. */
__attribute__((noinline)) u32 readiness(void) {
    u32 cb = U32(C.main + 4);
    return overworld() || (C.menus && cb && cb != C.battle_cb2) ? 0 : NOT_OVERWORLD;
}

/* Runs after ReadKeys and HandleLinkConnection, exactly once. RfuMain1 draws
 * Random before callback1 even with its manager shut down. The default
 * post-VBlank offsets (Mewtwo 3, birds 5) include the RFU draw on every
 * script pass, plus the VBlanks between the script's native yields.
 * Require that exact successor; extra draws / reseeds still cancel the A. */
__attribute__((noinline)) void press_shim(void) {
    u32 ime = U16(0x04000208);
    U16(0x04000208) = 0;
    U32(S.call_slot) = S.call_original;
    if (S.status == PENDING) {
        u32 reason = U32(C.rng) != step(S.seed) ? RNG_CHANGED
            : U32(C.main + 4) != S.call_context ? NOT_OVERWORLD : readiness();
        if (!reason) {
            S.status = FIRED;
            /* Walking consumes heldKeys; menu / script confirmation uses newKeys.
             * ReadKeys replaces both on the next loop, making this one input. */
            u32 button = C.button;
            U32(C.main + 0x2C) |= button | (button << 16);
        } else miss(reason);
    }
    U16(0x04000208) = ime;
    ((callback)S.call_original)();
}

static u32 nature_of(u32 lo, u32 hi) {
    u32 n = lo + hi * 11;
    n -= ((n * 5242) >> 17) * 25;
    while (n >= 25) n -= 25;
    return n;
}

__attribute__((noinline)) int matches(u32 seed) {
    u32 a, lo, hi;
    if (C.model) {
        if (!S.work_active) {
            a = step(seed);
            u32 n = a >> 16;
            if (C.model == 2) {
                n -= ((n * 5242) >> 19) * 100;
                while (n >= 100) n -= 100;
                static const u8 ends[11] = {20, 40, 50, 60, 70, 80, 85, 90, 94, 98, 99};
                u32 slot = 0;
                while (slot < 11 && n >= ends[slot]) ++slot;
                S.work_nature = C.letters[slot];
                a = step(a);
            } else {
                a = step(step(a)); /* slot, level, nature; no Synchronize in FRLG */
                S.work_nature = nature_of(a >> 16, 0);
                if (C.nature != 255 && S.work_nature != C.nature) return 0;
            }
            S.work_cursor = a; S.work_active = 1;
        }
        a = S.work_cursor;
        /* Resume difficult candidates next VBlank instead of an unbounded IRQ loop. */
        for (u32 count = 0; count < 8; ++count) {
            a = step(a); lo = a >> 16;
            a = step(a); hi = a >> 16;
            if (C.model == 2) { u32 t = lo; lo = hi; hi = t; }
            u32 n = nature_of(lo, hi);
            if (C.model == 2) {
                n = (lo & 3) | ((lo >> 6) & 12) | ((hi << 4) & 48) | ((hi >> 2) & 192);
                while (n >= 28) n -= 28;
            }
            if (n == S.work_nature) { S.work_active = 0; goto rolled; }
        }
        S.work_cursor = a;
        return -1;
    }
    a = step(seed); lo = a >> 16;
    a = step(a); hi = a >> 16;
rolled:
    u32 ids = U32(C.sb2ptr);
    if (C.shiny && (lo ^ hi ^ U16(ids + 10) ^ U16(ids + 12)) >= 8) return 0;
    if (C.nature != 255) {
        if (nature_of(lo, hi) != C.nature) return 0;
    }
    if (C.method == 2) a = step(a);
    a = step(a);
    u32 ivs = (a >> 16) & 0x7FFF;
    if (C.method == 4) a = step(a);
    a = step(a);
    ivs |= (a >> 16) << 15;
    for (u32 i = 0; i < 6; ++i, ivs >>= 5) {
        u32 value = ivs & 31;
        if (value < C.minimum[i] || value > C.maximum[i]) return 0;
    }
    return 1;
}

static const u16 font[16] = {0x7B6F, 0x749A, 0x73E7, 0x79E7, 0x49ED, 0x79CF, 0x7BCF, 0x4927,
    0x7BEF, 0x79EF, 0x5BEF, 0x3AEB, 0x724F, 0x3B6B, 0x73CF, 0x13CF};
static u32 bcd(u32 n) {
    u32 result = 0;
    for (u32 i = 0; i < 24; ++i) {
        result += 0x33333333;
        result -= ((~result >> 3) & 0x11111111) * 3;
        result = (result << 1) | ((n >> 23) & 1);
        n <<= 1;
    }
    return result;
}

/* Eight 8x16 objects use the same final eight OAM slots as the upstream overlay.
 * Dynamic upper/lower tiles show all eight seed digits and a status + 7-digit count.
 */
__attribute__((noinline)) void tiles(void) {
    u32 values[2] = {S.seed, S.shown};
    u32 keys = U16(C.main + 0x2C);
    if ((keys & 0x300) == 0x300) {
        /* Pokemon starts with an unencrypted u32 PID; party entries are 100
         * bytes. The count is a byte, and must be checked before indexing. */
        u32 count = U8(C.party_count);
        if (count > 6) count = 0;
        values[0] = count ? U32(C.party + (count - 1) * 100) : 0xFFFFFFFF;
        values[1] = count;
    } else if (keys & 0x200) {
        values[0] = S.initial; values[1] = S.index < 10000000 ? bcd(S.index) : 0xFFFFFFFF;
    }
    for (u32 row = 0; row < 2; ++row) {
        for (u32 digit = 0; digit < 8; ++digit) {
            u32 bits = font[(values[row] >> 28) & 15];
            values[row] <<= 4;
            volatile u32 *tile = (volatile u32 *)(0x06017E00 + digit * 64 + row * 32);
            tile[0] = tile[6] = tile[7] = 0x22222222;
            for (u32 y = 1; y < 6; ++y) {
                u32 pixels = 0x22222222;
                pixels -= (bits & 1) << 8;
                pixels -= (bits & 2) << 11;
                pixels -= (bits & 4) << 14;
                bits >>= 3;
                tile[y] = pixels;
            }
        }
    }
}

__attribute__((section(".entry"), used)) void hook(void) {
    u32 idle = !(U16(C.main + 0x1C) & 1);
    /* A second interrupt before callback1 means the pending press has expired. */
    if (S.status == PENDING) {
        if (U32(S.call_slot) == (u32)press_shim) U32(S.call_slot) = S.call_original;
        miss(EXPIRED);
    }
    if (!readiness() && (S.status || overworld())) {
        for (u32 i = 0; i < 8; ++i) {
            u32 oam = C.main + 0x3F8 + i * 8;
            U16(oam) = 0x8002; U16(oam + 2) = 174 + i * 8; U16(oam + 4) = 0xF3F0 + i * 2;
        }
    }
    ((callback)C.original)();
    if (!S.status) {
        if (!overworld()) return;
        S.initial = ((u16 (*)(void))C.seed_getter)();
        S.cursor = S.initial * C.jump_a + C.jump_c;
        S.next = C.first;
        S.status = SEARCH;
    }
    S.seed = U32(C.rng);
    u32 index = distance(S.initial, S.seed);
    u32 delta = index - S.index;
    if (index < S.index || index > 9999999 || S.initial != ((u16 (*)(void))C.seed_getter)()) S.status = DESYNC;
    S.index = index;
    u32 reason = readiness();
    u32 stable = idle && delta == 2 && !reason;
    /* Keep the reason visible for 60 eligible frames before looking ahead again.
     * Static map profiles retain the notice in menus; tracking continues throughout.
     * Catch-up rebases from the live RNG, within the original range / epoch. */
    if (S.status == MISSED && !S.notice && idle && !reason) {
        ++S.next; S.cursor = step(S.cursor); S.locked = 0; S.status = SEARCH;
        S.work_active = 0;
    }
    if (S.status == FOUND) {
        u32 press = S.target - C.offset;
        /* The visible target is fixed: a single observed stride cannot predict
         * future strides. An actual miss shows its notice before retrying. */
        if (S.index > press) miss(PASSED);
        else if (S.index == press) {
            if (idle && !reason) {
                S.call_slot = C.main + (overworld() ? 0 : 4);
                S.call_original = U32(S.call_slot); S.call_context = U32(C.main + 4);
                S.status = PENDING; U32(S.call_slot) = (u32)press_shim;
            }
            else miss(idle ? reason : LAG);
        }
    }
    if (S.status == SEARCH && idle && !reason) {
        if (S.next <= S.index + C.offset) {
            S.next = S.index + C.offset + 1;
            S.cursor = S.seed * C.offset_a + C.offset_c;
            S.work_active = 0;
        }
        for (u32 count = 0; count < 16; ++count) {
            if (S.next > C.last) { S.status = EXHAUSTED; break; }
            int match = (!stable || !((S.next - C.offset - S.index) & 1)) ? matches(S.cursor) : 0;
            if (match < 0) break;
            if (match) {
                S.target = S.next; S.generation = S.cursor; S.locked = 1; S.status = FOUND; break;
            }
            ++S.next; S.cursor = step(S.cursor);
            S.work_active = 0;
        }
        if (S.status == SEARCH && S.next > C.last) S.status = EXHAUSTED;
    }
    u32 display = S.status;
    u32 n = 0;
    if (display == SEARCH || display == FOUND) S.reason = reason;
    if (display == SEARCH) { display = 10; n = S.next; }
    else if (display == FOUND) {
        display = 11;
        n = S.target - C.offset - S.index;
    }
    else if (display == FIRED || display == PENDING) { n = display == PENDING; display = 12; }
    else if (display == MISSED) { display = 13; n = S.reason; }
    else if (display == EXHAUSTED) display = 14;
    else display = 15;
    S.shown = (display << 28) | bcd(n);
    if (!reason) {
        u32 keys = U16(C.main + 0x2C);
        if (S.status == MISSED && S.notice && !(keys & 0x200)) --S.notice;
        u32 color = (keys & 0x300) == 0x300 ? 0x7FFF : S.status == MISSED ? 0x001F
            : S.status == FOUND
                ? (reason || ((S.target - C.offset - S.index) & 1) ? 0x02FF : 0x03E0) : 0x7FFF;
        U16(C.palette) = U16(C.palette - 0x400) = color;
        U16(C.palette + 2) = U16(C.palette - 0x3FE) = 0;
        tiles();
    }
}
