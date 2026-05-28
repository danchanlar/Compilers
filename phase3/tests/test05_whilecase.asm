.text
.globl main
main:
    addi sp, sp, -36
    mv gp, sp
    j L_2

L_1:
    # 1: begin_block, test05whilecase, _, _
    # begin main block

L_2:
    # 2: :=, 1, _, x
    li t1, 1
    addi t0, gp, 16
    sw t1, 0(t0)

L_3:
    # 3: :=, 0, _, sum
    li t1, 0
    addi t0, gp, 20
    sw t1, 0(t0)

L_4:
    # 4: if<, x, 4, 5
    addi t1, gp, 16
    lw t1, 0(t1)
    li t2, 4
    blt t1, t2, L_6

L_5:
    # 5: jump, _, _, 10
    j L_11

L_6:
    # 6: +, sum, x, T_1
    addi t1, gp, 20
    lw t1, 0(t1)
    addi t2, gp, 16
    lw t2, 0(t2)
    add t1, t1, t2
    addi t0, gp, 24
    sw t1, 0(t0)

L_7:
    # 7: :=, T_1, _, sum
    addi t1, gp, 24
    lw t1, 0(t1)
    addi t0, gp, 20
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
    # 10: jump, _, _, 3
    j L_4

L_11:
    # 11: +, sum, 100, T_3
    addi t1, gp, 20
    lw t1, 0(t1)
    li t2, 100
    add t1, t1, t2
    addi t0, gp, 32
    sw t1, 0(t0)

L_12:
    # 12: :=, T_3, _, sum
    addi t1, gp, 32
    lw t1, 0(t1)
    addi t0, gp, 20
    sw t1, 0(t0)

L_13:
    # 13: out, sum, _, _
    addi a0, gp, 20
    lw a0, 0(a0)
    li a7, 1
    ecall
    li a0, 10
    li a7, 11
    ecall

L_14:
    # 14: halt, _, _, _
    li a7, 10
    ecall

L_15:
    # 15: end_block, test05whilecase, _, _
    li a7, 10
    ecall

