.text
.globl main
main:
    addi sp, sp, -32
    mv gp, sp
    j L_2

L_1:
    # 1: begin_block, test08forcase, _, _
    # begin main block

L_2:
    # 2: :=, 0, _, sum
    li t1, 0
    addi t0, gp, 20
    sw t1, 0(t0)

L_3:
    # 3: :=, 1, _, i
    li t1, 1
    addi t0, gp, 16
    sw t1, 0(t0)

L_4:
    # 4: if>, i, 5, 11
    addi t1, gp, 16
    lw t1, 0(t1)
    li t2, 5
    bgt t1, t2, L_12

L_5:
    # 5: if<=, i, 5, 6
    addi t1, gp, 16
    lw t1, 0(t1)
    li t2, 5
    ble t1, t2, L_7

L_6:
    # 6: jump, _, _, 8
    j L_9

L_7:
    # 7: +, sum, i, T_1
    addi t1, gp, 20
    lw t1, 0(t1)
    addi t2, gp, 16
    lw t2, 0(t2)
    add t1, t1, t2
    addi t0, gp, 24
    sw t1, 0(t0)

L_8:
    # 8: :=, T_1, _, sum
    addi t1, gp, 24
    lw t1, 0(t1)
    addi t0, gp, 20
    sw t1, 0(t0)

L_9:
    # 9: +, i, 1, T_2
    addi t1, gp, 16
    lw t1, 0(t1)
    li t2, 1
    add t1, t1, t2
    addi t0, gp, 28
    sw t1, 0(t0)

L_10:
    # 10: :=, T_2, _, i
    addi t1, gp, 28
    lw t1, 0(t1)
    addi t0, gp, 16
    sw t1, 0(t0)

L_11:
    # 11: jump, _, _, 3
    j L_4

L_12:
    # 12: out, sum, _, _
    addi a0, gp, 20
    lw a0, 0(a0)
    li a7, 1
    ecall
    li a0, 10
    li a7, 11
    ecall

L_13:
    # 13: halt, _, _, _
    li a7, 10
    ecall

L_14:
    # 14: end_block, test08forcase, _, _
    li a7, 10
    ecall

