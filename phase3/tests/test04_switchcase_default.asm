.text
.globl main
main:
    addi sp, sp, -24
    mv gp, sp
    j L_2

L_1:
    # 1: begin_block, test04switchcase, _, _
    # begin main block

L_2:
    # 2: :=, 3, _, x
    li t1, 3
    addi t0, gp, 16
    sw t1, 0(t0)

L_3:
    # 3: :=, 0, _, y
    li t1, 0
    addi t0, gp, 20
    sw t1, 0(t0)

L_4:
    # 4: if=, x, 1, 5
    addi t1, gp, 16
    lw t1, 0(t1)
    li t2, 1
    beq t1, t2, L_6

L_5:
    # 5: jump, _, _, 7
    j L_8

L_6:
    # 6: :=, 10, _, y
    li t1, 10
    addi t0, gp, 20
    sw t1, 0(t0)

L_7:
    # 7: jump, _, _, 12
    j L_13

L_8:
    # 8: if=, x, 2, 9
    addi t1, gp, 16
    lw t1, 0(t1)
    li t2, 2
    beq t1, t2, L_10

L_9:
    # 9: jump, _, _, 11
    j L_12

L_10:
    # 10: :=, 20, _, y
    li t1, 20
    addi t0, gp, 20
    sw t1, 0(t0)

L_11:
    # 11: jump, _, _, 12
    j L_13

L_12:
    # 12: :=, 99, _, y
    li t1, 99
    addi t0, gp, 20
    sw t1, 0(t0)

L_13:
    # 13: out, y, _, _
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
    # 15: end_block, test04switchcase, _, _
    li a7, 10
    ecall

