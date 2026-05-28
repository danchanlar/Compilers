.text
.globl main
main:
    addi sp, sp, -36
    mv gp, sp
    j L_2

L_1:
    # 1: begin_block, test06incase, _, _
    # begin main block

L_2:
    # 2: :=, 0, _, x
    li t1, 0
    addi t0, gp, 16
    sw t1, 0(t0)

L_3:
    # 3: :=, 0, _, y
    li t1, 0
    addi t0, gp, 20
    sw t1, 0(t0)

L_4:
    # 4: :=, 0, _, T_1
    li t1, 0
    addi t0, gp, 24
    sw t1, 0(t0)

L_5:
    # 5: if<, x, 3, 6
    addi t1, gp, 16
    lw t1, 0(t1)
    li t2, 3
    blt t1, t2, L_7

L_6:
    # 6: jump, _, _, 9
    j L_10

L_7:
    # 7: :=, 1, _, T_1
    li t1, 1
    addi t0, gp, 24
    sw t1, 0(t0)

L_8:
    # 8: +, x, 1, T_2
    addi t1, gp, 16
    lw t1, 0(t1)
    li t2, 1
    add t1, t1, t2
    addi t0, gp, 28
    sw t1, 0(t0)

L_9:
    # 9: :=, T_2, _, x
    addi t1, gp, 28
    lw t1, 0(t1)
    addi t0, gp, 16
    sw t1, 0(t0)

L_10:
    # 10: if<, y, 2, 11
    addi t1, gp, 20
    lw t1, 0(t1)
    li t2, 2
    blt t1, t2, L_12

L_11:
    # 11: jump, _, _, 14
    j L_15

L_12:
    # 12: :=, 1, _, T_1
    li t1, 1
    addi t0, gp, 24
    sw t1, 0(t0)

L_13:
    # 13: +, y, 1, T_3
    addi t1, gp, 20
    lw t1, 0(t1)
    li t2, 1
    add t1, t1, t2
    addi t0, gp, 32
    sw t1, 0(t0)

L_14:
    # 14: :=, T_3, _, y
    addi t1, gp, 32
    lw t1, 0(t1)
    addi t0, gp, 20
    sw t1, 0(t0)

L_15:
    # 15: if=, T_1, 1, 3
    addi t1, gp, 24
    lw t1, 0(t1)
    li t2, 1
    beq t1, t2, L_4

L_16:
    # 16: out, x, _, _
    addi a0, gp, 16
    lw a0, 0(a0)
    li a7, 1
    ecall
    li a0, 10
    li a7, 11
    ecall

L_17:
    # 17: out, y, _, _
    addi a0, gp, 20
    lw a0, 0(a0)
    li a7, 1
    ecall
    li a0, 10
    li a7, 11
    ecall

L_18:
    # 18: halt, _, _, _
    li a7, 10
    ecall

L_19:
    # 19: end_block, test06incase, _, _
    li a7, 10
    ecall

