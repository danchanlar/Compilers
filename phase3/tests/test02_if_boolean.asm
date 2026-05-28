.text
.globl main
main:
    addi sp, sp, -28
    mv gp, sp
    j L_2

L_1:
    # 1: begin_block, test02ifbool, _, _
    # begin main block

L_2:
    # 2: :=, 5, _, a
    li t1, 5
    addi t0, gp, 16
    sw t1, 0(t0)

L_3:
    # 3: :=, 10, _, b
    li t1, 10
    addi t0, gp, 20
    sw t1, 0(t0)

L_4:
    # 4: :=, 0, _, c
    li t1, 0
    addi t0, gp, 24
    sw t1, 0(t0)

L_5:
    # 5: if<, a, b, 6
    addi t1, gp, 16
    lw t1, 0(t1)
    addi t2, gp, 20
    lw t2, 0(t2)
    blt t1, t2, L_7

L_6:
    # 6: jump, _, _, 8
    j L_9

L_7:
    # 7: if>=, b, 10, 10
    addi t1, gp, 20
    lw t1, 0(t1)
    li t2, 10
    bge t1, t2, L_11

L_8:
    # 8: jump, _, _, 8
    j L_9

L_9:
    # 9: if=, a, 5, 12
    addi t1, gp, 16
    lw t1, 0(t1)
    li t2, 5
    beq t1, t2, L_13

L_10:
    # 10: jump, _, _, 10
    j L_11

L_11:
    # 11: :=, 1, _, c
    li t1, 1
    addi t0, gp, 24
    sw t1, 0(t0)

L_12:
    # 12: jump, _, _, 13
    j L_14

L_13:
    # 13: :=, 2, _, c
    li t1, 2
    addi t0, gp, 24
    sw t1, 0(t0)

L_14:
    # 14: out, c, _, _
    addi a0, gp, 24
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
    # 16: end_block, test02ifbool, _, _
    li a7, 10
    ecall

