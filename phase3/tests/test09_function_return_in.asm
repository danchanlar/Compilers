.text
.globl main
main:
    addi sp, sp, -32
    mv gp, sp
    j L_8

L_1:
    # 1: begin_block, test09funcret, _, _
    # begin main block
    j L_8

L_2:
    # 2: begin_block, addmul, _, _
    # begin function addmul
    sw ra, 8(sp)

L_3:
    # 3: *, y, 2, T_1
    addi t1, sp, 20
    lw t1, 0(t1)
    li t2, 2
    mul t1, t1, t2
    addi t0, sp, 28
    sw t1, 0(t0)

L_4:
    # 4: +, x, T_1, T_2
    addi t1, sp, 16
    lw t1, 0(t1)
    addi t2, sp, 28
    lw t2, 0(t2)
    add t1, t1, t2
    addi t0, sp, 32
    sw t1, 0(t0)

L_5:
    # 5: :=, T_2, _, z
    addi t1, sp, 32
    lw t1, 0(t1)
    addi t0, sp, 24
    sw t1, 0(t0)

L_6:
    # 6: retv, z, _, _
    addi t1, sp, 24
    lw t1, 0(t1)
    lw t0, 0(sp)
    sw t1, 0(t0)
    j L_7

L_7:
    # 7: end_block, addmul, _, _
    # end function addmul
    lw ra, 8(sp)
    jr ra

L_8:
    # 8: :=, 4, _, a
    li t1, 4
    addi t0, gp, 16
    sw t1, 0(t0)

L_9:
    # 9: :=, 6, _, b
    li t1, 6
    addi t0, gp, 20
    sw t1, 0(t0)

L_10:
    # 10: par, a, CV, _

L_11:
    # 11: par, b, CV, _

L_12:
    # 12: par, T_3, RET, _

L_13:
    # 13: call, addmul, _, _
    # call addmul
    addi t0, sp, -36
    sw sp, 4(t0)
    mv t1, sp
    sw t1, 12(t0)
    addi t1, gp, 28
    sw t1, 0(t0)
    addi t1, gp, 16
    lw t1, 0(t1)
    sw t1, 16(t0)
    addi t1, gp, 20
    lw t1, 0(t1)
    sw t1, 20(t0)
    addi sp, sp, -36
    jal L_2
    addi sp, sp, 36

L_14:
    # 14: :=, T_3, _, r
    addi t1, gp, 28
    lw t1, 0(t1)
    addi t0, gp, 24
    sw t1, 0(t0)

L_15:
    # 15: out, r, _, _
    addi a0, gp, 24
    lw a0, 0(a0)
    li a7, 1
    ecall
    li a0, 10
    li a7, 11
    ecall

L_16:
    # 16: halt, _, _, _
    li a7, 10
    ecall

L_17:
    # 17: end_block, test09funcret, _, _
    li a7, 10
    ecall

