    .data
input:           .word  0x80
output:          .word  0x84
    .text
_start:
    addi     sp, zero, 0x7f                  ; Инициализация стека ровно перед вводом

    lui      t0, %hi(input)                  ; загружаем 20 бит (младшие) и сдвигаем влево на 12
    addi     t0, t0, %lo(input)              ; загружаем 12 бит (старшие)
    lw       t0, 0(t0)                       ; разыменовываем указатель input
    lw       a0, 0(t0)                       ; читаем число n по адресу 0x80

    jal      ra, compute_sum                 ; вызываем процедуру


    lui      t0, %hi(output)
    addi     t0, t0, %lo(output)
    lw       t0, 0(t0)                       ;загрузка
    sw       a0, 0(t0)                       ; сохранение
    halt


compute_sum:
    addi     sp, sp, -4                      ; выделяем место на стеке 4 т.к. размер записываемого слова 32 бита
    sw       ra, 0(sp)                       ; сохраняем ra

    ble      a0, zero, error1_proc           ; if (n <= 0) - проверка на невалидный ввод

    lui      t2, 0x10                        ; t2 = 65536
    bgt      a0, t2, overflow_proc           ; if (n > 65536) - проверка на переполнение

    addi     t2, a0, 1                       ; t2 = n + 1
    mul      t2, a0, t2                      ; t2 = n * (n+1)
    srli     a0, t2, 1                       ; делим пополам (сдвиг вправо)
    j        return_proc

error1_proc:
    addi     a0, zero, -1                    ; a0 = -1
    j        return_proc

overflow_proc:
    lui      t2, 0xccccc                     ; загружаем верхние биты
    addi     t2, t2, 0xccc                   ; прибавляем нижние
    mv       a0, t2                          ; a0 = 0xCCCCCCCC

return_proc:
    lw       ra, 0(sp)                       ; восстанавливаем ra
    addi     sp, sp, 4                       ; освобождаем стек
    jr       ra                              ; возврат