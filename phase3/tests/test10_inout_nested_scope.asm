.text
.globl main
main:
    addi sp, sp, -32
    mv gp, sp
    j L_17

L_1:
    # 1: begin_block, test10nested, _, _
    # begin main block
    j L_17

L_2:
    # 2: begin_block, outer, _, _
    # begin function outer
    sw ra, 8(sp)
    j L_8

L_3:
    # 3: begin_block, inner, _, _
    # begin function inner
    sw ra, 8(sp)

L_4:
    # 4: +, local, z, T_1
    mv t1, sp
    lw t1, 12(t1)
    addi t1, t1, 24
    lw t1, 0(t1)
    addi t2, sp, 16
    lw t2, 0(t2)
    add t1, t1, t2
    addi t0, sp, 20
    sw t1, 0(t0)

L_5:
    # 5: :=, T_1, _, local
    addi t1, sp, 20
    lw t1, 0(t1)
    mv t0, sp
    lw t0, 12(t0)
    addi t0, t0, 24
    sw t1, 0(t0)

L_6:
    # 6: retv, local, _, _
    mv t1, sp
    lw t1, 12(t1)
    addi t1, t1, 24
    lw t1, 0(t1)
    lw t0, 0(sp)
    sw t1, 0(t0)
    j L_7

L_7:
    # 7: end_block, inner, _, _
    # end function inner
    lw ra, 8(sp)
    jr ra

L_8:
    # 8: +, x, y, T_2
    addi t1, sp, 16
    lw t1, 0(t1)
    lw t2, 20(sp)
    lw t2, 0(t2)
    add t1, t1, t2
    addi t0, sp, 28
    sw t1, 0(t0)

L_9:
    # 9: :=, T_2, _, local
    addi t1, sp, 28
    lw t1, 0(t1)
    addi t0, sp, 24
    sw t1, 0(t0)

L_10:
    # 10: +, y, 1, T_3
    lw t1, 20(sp)
    lw t1, 0(t1)
    li t2, 1
    add t1, t1, t2
    addi t0, sp, 32
    sw t1, 0(t0)

L_11:
    # 11: :=, T_3, _, y
    addi t1, sp, 32
    lw t1, 0(t1)
    lw t0, 20(sp)
    sw t1, 0(t0)

L_12:
    # 12: par, y, CV, _

L_13:
    # 13: par, T_4, RET, _

L_14:
    # 14: call, inner, _, _
    # call inner
    addi t0, sp, -24
    sw sp, 4(t0)
    mv t1, sp
    sw t1, 12(t0)
    addi t1, sp, 36
    sw t1, 0(t0)
    lw t1, 20(sp)
    lw t1, 0(t1)
    sw t1, 16(t0)
    addi sp, sp, -24
    jal L_3
    addi sp, sp, 24

L_15:
    # 15: retv, T_4, _, _
    addi t1, sp, 36
    lw t1, 0(t1)
    lw t0, 0(sp)
    sw t1, 0(t0)
    j L_16

L_16:
    # 16: end_block, outer, _, _
    # end function outer
    lw ra, 8(sp)
    jr ra

L_17:
    # 17: :=, 5, _, a
    li t1, 5
    addi t0, gp, 16
    sw t1, 0(t0)

L_18:
    # 18: :=, 2, _, b
    li t1, 2
    addi t0, gp, 20
    sw t1, 0(t0)

L_19:
    # 19: par, a, CV, _

L_20:
    # 20: par, b, REF, _

L_21:
    # 21: par, T_5, RET, _

L_22:
    # 22: call, outer, _, _
    # call outer
    addi t0, sp, -40
    sw sp, 4(t0)
    mv t1, sp
    sw t1, 12(t0)
    addi t1, gp, 28
    sw t1, 0(t0)
    addi t1, gp, 16
    lw t1, 0(t1)
    sw t1, 16(t0)
    addi t1, gp, 20
    sw t1, 20(t0)
    addi sp, sp, -40
    jal L_2
    addi sp, sp, 40

L_23:
    # 23: :=, T_5, _, r
    addi t1, gp, 28
    lw t1, 0(t1)
    addi t0, gp, 24
    sw t1, 0(t0)

L_24:
    # 24: out, r, _, _
    addi a0, gp, 24
    lw a0, 0(a0)
    li a7, 1
    ecall
    li a0, 10
    li a7, 11
    ecall

L_25:
    # 25: out, b, _, _
    addi a0, gp, 20
    lw a0, 0(a0)
    li a7, 1
    ecall
    li a0, 10
    li a7, 11
    ecall

L_26:
    # 26: halt, _, _, _
    li a7, 10
    ecall

L_27:
    # 27: end_block, test10nested, _, _
    li a7, 10
    ecall

