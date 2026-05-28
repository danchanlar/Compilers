.text
.globl main
main:
    addi sp, sp, -60
    mv gp, sp
    j L_2

L_1:
    # 1: begin_block, test01arith, _, _
    # begin main block

L_2:
    # 2: :=, 2, _, a
    li t1, 2
    addi t0, gp, 16
    sw t1, 0(t0)

L_3:
    # 3: :=, 3, _, b
    li t1, 3
    addi t0, gp, 20
    sw t1, 0(t0)

L_4:
    # 4: :=, 4, _, c
    li t1, 4
    addi t0, gp, 24
    sw t1, 0(t0)

L_5:
    # 5: *, b, c, T_1
    addi t1, gp, 20
    lw t1, 0(t1)
    addi t2, gp, 24
    lw t2, 0(t2)
    mul t1, t1, t2
    addi t0, gp, 36
    sw t1, 0(t0)

L_6:
    # 6: +, a, T_1, T_2
    addi t1, gp, 16
    lw t1, 0(t1)
    addi t2, gp, 36
    lw t2, 0(t2)
    add t1, t1, t2
    addi t0, gp, 40
    sw t1, 0(t0)

L_7:
    # 7: +, a, b, T_3
    addi t1, gp, 16
    lw t1, 0(t1)
    addi t2, gp, 20
    lw t2, 0(t2)
    add t1, t1, t2
    addi t0, gp, 44
    sw t1, 0(t0)

L_8:
    # 8: -, T_2, T_3, T_4
    addi t1, gp, 40
    lw t1, 0(t1)
    addi t2, gp, 44
    lw t2, 0(t2)
    sub t1, t1, t2
    addi t0, gp, 48
    sw t1, 0(t0)

L_9:
    # 9: :=, T_4, _, d
    addi t1, gp, 48
    lw t1, 0(t1)
    addi t0, gp, 28
    sw t1, 0(t0)

L_10:
    # 10: -, 0, d, T_5
    li t1, 0
    addi t2, gp, 28
    lw t2, 0(t2)
    sub t1, t1, t2
    addi t0, gp, 52
    sw t1, 0(t0)

L_11:
    # 11: +, T_5, 10, T_6
    addi t1, gp, 52
    lw t1, 0(t1)
    li t2, 10
    add t1, t1, t2
    addi t0, gp, 56
    sw t1, 0(t0)

L_12:
    # 12: :=, T_6, _, e
    addi t1, gp, 56
    lw t1, 0(t1)
    addi t0, gp, 32
    sw t1, 0(t0)

L_13:
    # 13: out, d, _, _
    addi a0, gp, 28
    lw a0, 0(a0)
    li a7, 1
    ecall
    li a0, 10
    li a7, 11
    ecall

L_14:
    # 14: out, e, _, _
    addi a0, gp, 32
    lw a0, 0(a0)
    li a7, 1
    ecall
    li a0, 10
    li a7, 11
    ecall

L_15:
    # 15: halt, _, _, _
    li a7, 10
    ecall

L_16:
    # 16: end_block, test01arith, _, _
    li a7, 10
    ecall

