/* SPDX-License-Identifier: AGPL-3.0-or-later
 * Natural Method-1 search. No store to gRngValue, Pokemon, saves, scripts or ROM.
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
    u32 main, rng, sb2ptr, cb1, cb2, original, context, wait, objects, selected, seed_getter, palette;
    u32 first, last, jump_a, jump_c;
    u8 graphics, offset, shiny, nature, minimum[6], maximum[6];
};
__attribute__((section(".config"), used)) volatile struct Config config = {0};
enum { WAIT, SEARCH, FOUND, EXHAUSTED, MISSED, DESYNC, PENDING, FIRED };
/* Keep existing timing / Mewtwo reason numbers; retired bird gates have no code. */
enum { SCRIPT = 3, NOT_OVERWORLD, NO_TARGET, PASSED = 9, LAG, RNG_CHANGED, EXPIRED };
struct State { u32 initial, seed, index, cursor, next, target, generation, shown, status, reason, locked, notice; };
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

/* Birds send A at the deadline; the user is responsible for positioning.
 * Mewtwo retains its measured script-button-wait timing profile. */
__attribute__((noinline)) u32 readiness(void) {
    if (!overworld()) return NOT_OVERWORLD;
    if (C.offset != 1) return 0;
    u32 object = U8(C.selected);
    if (U8(C.context + 1) != 2 || U32(C.context + 4) != C.wait) return SCRIPT;
    return object < 16
        && (U8(C.objects + object * 36) & 1)
        && U8(C.objects + object * 36 + 5) == C.graphics ? 0 : NO_TARGET;
}

/* Runs after ReadKeys, exactly once; stale callbacks never inject a late A. */
__attribute__((noinline)) void press_shim(void) {
    u32 ime = U16(0x04000208);
    U16(0x04000208) = 0;
    U32(C.main) = C.cb1;
    if (S.status == PENDING) {
        u32 reason = U32(C.rng) != S.seed ? RNG_CHANGED : readiness();
        if (!reason) {
            S.status = FIRED;
            U16(C.main + 0x2E) |= 1;
        } else miss(reason);
    }
    U16(0x04000208) = ime;
    ((callback)C.cb1)();
}

__attribute__((noinline)) int matches(u32 seed) {
    u32 a = step(seed), lo = a >> 16;
    a = step(a);
    u32 hi = a >> 16;
    u32 ids = U32(C.sb2ptr);
    if (C.shiny && (lo ^ hi ^ U16(ids + 10) ^ U16(ids + 12)) >= 8) return 0;
    if (C.nature != 255) {
        u32 n = lo + hi * 11;
        n -= ((n * 5242) >> 17) * 25;
        while (n >= 25) n -= 25;
        if (n != C.nature) return 0;
    }
    a = step(a);
    u32 ivs = (a >> 16) & 0x7FFF;
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
static const u32 powers[7] = {1000000, 100000, 10000, 1000, 100, 10, 1};
static u32 bcd(u32 n) {
    u32 result = 0;
    for (u32 i = 0; i < 7; ++i) {
        u32 digit = 0;
        while (n >= powers[i]) { n -= powers[i]; ++digit; }
        result = (result << 4) | digit;
    }
    return result;
}

/* Eight 8x16 objects use the same final eight OAM slots as the upstream overlay.
 * Dynamic upper/lower tiles show all eight seed digits and a status + 7-digit count.
 */
__attribute__((noinline)) void tiles(void) {
    u32 values[2] = {S.seed, S.shown};
    if (U16(C.main + 0x2C) & 0x200) {
        values[0] = S.initial; values[1] = S.index < 10000000 ? bcd(S.index) : 0xFFFFFFFF;
    }
    for (u32 row = 0; row < 2; ++row) {
        for (u32 digit = 0; digit < 8; ++digit) {
            u32 bits = font[(values[row] >> 28) & 15];
            values[row] <<= 4;
            volatile u32 *tile = (volatile u32 *)(0x06017E00 + digit * 64 + row * 32);
            for (u32 y = 0; y < 8; ++y) {
                u32 pixels = 0x22222222;
                if (y && y < 6) {
                    pixels -= (bits & 1) << 8;
                    pixels -= (bits & 2) << 11;
                    pixels -= (bits & 4) << 14;
                    bits >>= 3;
                }
                tile[y] = pixels;
            }
        }
    }
}

__attribute__((section(".entry"), used)) void hook(void) {
    u32 idle = !(U16(C.main + 0x1C) & 1);
    /* A second interrupt before callback1 means the pending press has expired. */
    if (S.status == PENDING) {
        if (U32(C.main) == (u32)press_shim) U32(C.main) = C.cb1;
        miss(EXPIRED);
    }
    if (U32(C.main + 4) == C.cb2) {
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
    /* Keep the reason visible for 60 map frames before looking ahead again.
     * TV / menus do not consume that notice; tracking continues throughout.
     * Catch-up rebases from the live RNG, within the original range / epoch. */
    if (S.status == MISSED && !S.notice && idle && overworld()) {
        ++S.next; S.cursor = step(S.cursor); S.locked = 0; S.status = SEARCH;
    }
    if (S.status == FOUND) {
        u32 press = S.target - C.offset;
        /* Check initial two-call parity before showing B. Once the countdown is
         * visible its target is fixed: a single observed stride cannot predict
         * future strides. An actual miss shows its notice before retrying. */
        if (S.index > press) miss(PASSED);
        else if (S.index == press) {
            if (idle && !reason) { S.status = PENDING; U32(C.main) = (u32)press_shim; }
            else miss(idle ? reason : LAG);
        } else if (!S.locked && idle) {
            if (stable && ((press - S.index) & 1)) {
                ++S.next; S.cursor = step(S.cursor); S.status = SEARCH;
            } else S.locked = 1;
        }
    }
    if (S.status == SEARCH && idle && overworld()) {
        if (S.next <= S.index + C.offset) {
            S.next = S.index + C.offset + 1;
            S.cursor = step(S.seed);
            for (u32 i = 0; i < C.offset; ++i) S.cursor = step(S.cursor);
        }
        for (u32 count = 0; count < 16; ++count) {
            if (S.next > C.last) { S.status = EXHAUSTED; break; }
            if ((!stable || !((S.next - C.offset - S.index) & 1)) && matches(S.cursor)) {
                S.target = S.next; S.generation = S.cursor; S.locked = stable; S.status = FOUND; break;
            }
            ++S.next; S.cursor = step(S.cursor);
        }
        if (S.status == SEARCH && S.next > C.last) S.status = EXHAUSTED;
    }
    u32 display = S.status;
    u32 n = 0;
    if (display == SEARCH || display == FOUND) S.reason = reason;
    if (display == SEARCH) { display = 10; n = S.next; }
    else if (display == FOUND) {
        display = S.locked ? 11 : 10;
        n = S.locked ? S.target - C.offset - S.index : S.next;
    }
    else if (display == FIRED || display == PENDING) { n = display == PENDING; display = 12; }
    else if (display == MISSED) { display = 13; n = S.reason; }
    else if (display == EXHAUSTED) display = 14;
    else display = 15;
    S.shown = (display << 28) | bcd(n);
    if (U32(C.main + 4) == C.cb2) {
        if (S.status == MISSED && S.notice && !(U16(C.main + 0x2C) & 0x200)) --S.notice;
        u32 color = S.status == MISSED ? 0x001F
            : S.status == FOUND && S.locked
                ? (reason || ((S.target - C.offset - S.index) & 1) ? 0x02FF : 0x03E0) : 0x7FFF;
        U16(C.palette) = U16(C.palette - 0x400) = color;
        U16(C.palette + 2) = U16(C.palette - 0x3FE) = 0;
        tiles();
    }
}
