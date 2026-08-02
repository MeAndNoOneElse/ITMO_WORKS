.text
.org 0x88
_start:
    addi t0, zero, 0x80 / addi a1, zero, 0x84 / nop          / nop                          ; t0=(0x80), a1=(0x84)
    addi t2, zero, 0    / addi t3, zero, 0    / lw t1, 0(t0) / blt t1, zero, error_negative ; t2=sum=0, t3=sq=0, t1 = N ,N<0→ошибка
    mv a3, sp           / addi s1, zero, -1   / nop          / beqz t1, output              ; a3= стек, s1=-1 (для XOR ~), N==0→вывод нулей

read_loop:
    nop                 / nop                 / lw t5, 0(t0) / nop                          ; t5 = x[i] из MMIO
    nop                 / nop                 / sw t5, 0(sp) / nop                          ; сохраняем x[i] в стек
    addi sp, sp, 4      / addi t4, t4, 1      / nop          / blt t4, t1, read_loop        ; sp+=4, i++, если i<N→повтор

    addi t4, zero, 0    / mv sp, a3           / nop          / nop                          ; сброс i=0, sp→начало массива
    nop                 / nop                 / lw t5, 0(sp) / nop                          ; t5=x[0]

calc_loop:
    mul t6, t5, t5      / mulh a0, t5, t5     / nop          / nop                          ; t6=x²(lo), a0=x²(hi)
    mv s0fp, t2         / mv s5, t5           / nop          / bnez a0, overflow_error      ; сохраняем total, сохраняем x, если старшие не=0 то переполнение
    add a6, a0, zero    / add t3, t3, t6      / lw t5, 4(sp) / blt t3, zero, overflow_error ;  копируем mulh в a6 чтобы знак проверить, sq_total += x², prefetch следующего x[i+1], если sq_total стал отрицательным → переполнение
    add t2, t2, s5      / xor s2, s0fp, s5    / nop          / nop                          ; sum+=x, s2=old_sum XOR x (знаки одинаковы если ≥0)
    xor s3, s2, s1      / xor a0, s0fp, t2    / nop          / blt s2, zero, calc_next      ; s3=~s2, a0=old_sum XOR new_sum, разные знаки - ок
    and s4, s3, a0      / nop                 / nop          / nop                          ; s4=один.знак AND знак_сменился,

calc_next:
    addi t4, t4, 1      / addi sp, sp, 4      / nop          / blt t4, t1, calc_loop        ; i++, sp+=4, если i<N-продолжить

output:
    nop                 / nop                 / sw t2, 0(a1) / nop                          ; вывод sum(x)
    nop                 / nop                 / sw t3, 0(a1) / j done                       ; вывод sum(x²)

error_negative:
    addi t2, zero, -1   / nop                 / nop          / nop
    nop                 / nop                 / sw t2, 0(a1) / j done                       ; вывод -1 в MMIO

overflow_error:
    lui t2, 0xccccc     / nop                 / nop          / nop
    addi t2, t2, 0xccc  / nop                 / nop          / nop
    nop                 / nop                 / sw t2, 0(a1) / j done                       ; вывод 0xCCCCCCCC

done:
    nop                 / nop                 / nop          / halt                         ; останов
