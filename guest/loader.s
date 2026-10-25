@ SPDX-License-Identifier: AGPL-3.0-or-later
@ Position-independent Mystery Gift ARM entry and THUMB body.
@ Leads copy an inert chunk. Only the final image, after a full FNV-1a check,
@ publishes the hook with interrupts disabled. An existing hook is refused.
    .syntax unified
    .arch armv4t
    .arm
    .text
    .global _start
_start:
    b .Lcode
    .global p_dest, p_size, p_table, p_original, p_getter, p_game
    .global p_final, p_image_size, p_hash, p_entry, p_source, p_base
p_dest:       .word 0
p_size:       .word 0
p_table:      .word 0
p_original:   .word 0
p_getter:     .word 0
p_game:       .word 0
p_final:      .word 0
p_image_size: .word 0
p_hash:       .word 0
p_entry:      .word 0
p_source:     .word 0
p_base:       .word 0
.Lcode:
    add r3, pc, #1
    bx r3
    .thumb
    .thumb_func
.Lthumb:
    push {r4, r5, r6, r7, lr}
    movs r7, r0
.Lhere:
    mov r4, pc
    subs r4, #.Lhere + 4 - _start
    ldr r0, .Lheader
    ldr r1, [r0]
    ldr r2, [r4, #24]
    cmp r1, r2
    bne .Lgame_error
    ldrb r1, [r0, #16]
    cmp r1, #10
    bne .Lrevision_error
    ldr r0, [r4, #12]
    ldr r1, [r0]
    ldr r2, [r4, #16]
    cmp r1, r2
    bne .Lhook_error
    ldr r0, [r4, #20]
    ldr r1, [r0]
    ldr r2, .Lgetter_code
    cmp r1, r2
    bne .Lgetter_error
    ldrh r1, [r0, #4]
    ldr r2, .Lbx_lr
    cmp r1, r2
    bne .Lgetter_error
    ldr r1, [r0, #8]
    ldr r2, .Ltrainer_id
    cmp r1, r2
    bne .Lgetter_error
    ldr r5, [r4, #4]
    ldr r0, [r4, #8]
    ldr r6, [r4, #44]
    adds r6, r4, r6
.Lcopy:
    subs r0, #4
    bmi .Lcopied
    ldr r1, [r6, r0]
    str r1, [r5, r0]
    b .Lcopy
.Lcopied:
    ldr r0, [r4, #28]
    cmp r0, #0
    beq .Lok
    ldr r0, [r4, #48]
    ldr r1, [r4, #32]
    ldr r2, .Lfnv_basis
    ldr r3, .Lfnv_prime
.Lhash:
    ldrb r5, [r0]
    adds r0, #1
    eors r2, r5
    muls r2, r3
    subs r1, #1
    bne .Lhash
    ldr r0, [r4, #36]
    cmp r0, r2
    bne .Lhash_error
    ldr r5, .Lime
    ldrh r6, [r5]
    movs r0, #0
    strh r0, [r5]
    ldr r0, [r4, #12]
    ldr r1, [r0]
    ldr r2, [r4, #16]
    cmp r1, r2
    bne .Latomic_error
    ldr r1, [r4, #40]
    str r1, [r0]
    strh r6, [r5]
.Lok:
    ldr r0, .Lack
    b .Lreturn
.Latomic_error:
    strh r6, [r5]
.Lhook_error:
    movs r0, #3
    b .Lerror
.Lgame_error:
    movs r0, #1
    b .Lerror
.Lrevision_error:
    movs r0, #2
    b .Lerror
.Lgetter_error:
    movs r0, #4
    b .Lerror
.Lhash_error:
    movs r0, #5
.Lerror:
    ldr r1, .Lbad
    adds r0, r1
.Lreturn:
    str r0, [r7]
    movs r0, #1
    pop {r4, r5, r6, r7}
    pop {r3}
    bx r3
    .align 2
.Lheader:      .word 0x080000AC
.Lgetter_code: .word 0x88004801
.Lbx_lr:       .word 0x4770
.Ltrainer_id:  .word 0x02020000
.Lime:         .word 0x04000208
.Lfnv_basis:   .word 0x811C9DC5
.Lfnv_prime:   .word 0x01000193
.Lack:         .word 0x524E4703
.Lbad:         .word 0xBAD00000
