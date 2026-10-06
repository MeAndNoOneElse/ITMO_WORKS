    .data
buff:            .byte  '________________________________'
space:           .byte  '____'

input:           .word  0x80               ;ввод
output:          .word  0x84               ;вывод

first_char:      .word  0x0                ;ячейка для сохраниние порвого значения
second_char:     .word  0x0                ;ячейка для сохраниние второго значения
count_right:     .word  0x00               ;правый указатель
count_left:      .word  0x0                ;левый указатель
count_0:         .word  0x0                ;указатель на 0

one:             .word  0x1
ten:             .word  0x0A
twenty:          .word  0x20
o:               .word  0x0

fff0:            .word  0xffffff00
o00f:            .word  0x000000ff
F5F0000:         .word  0x5F5F0000
F5F5F500:        .word  0x5f5f5f00

    .text
    .org         0x88
_start:
_cycl:
    load_addr    count_right                 ;берём правый указатель
    sub          twenty                      ; если он больше 20, то это переполнение
    beqz         _c

    load_addr    input                       ;получаем адрес
    load_acc                                 ; получаем значение
    sub          o                           ;выставляем флаги
    beqz         _oo                         ;если записали 00, то надо сохранить текущий count_right в count_0
_pause:
 ;метка, чтобы вернуться

    store_addr   first_char                  ;временно сохраняем
    sub          ten                         ; проверяем, не конец ли это строки
    beqz         _prog_start                 ;и если да, то переходим к основной программе



    load_addr    first_char                  ; возвращаем обратно символ
    or           F5F0000                     ;берём только нужные биты в слове
    store_ind    count_right                 ; сохраняем в буфере по указателю
    load_addr    count_right                 ; берём сам указатель (адрес)
    add          one                         ; инкрементируем и сохраняем
    store_addr   count_right
    jmp          _cycl


_prog_start:
    load_addr    count_0
    beqz         _take_count_right           ;  если count_0 == 0, то надо в него записать count_right
    jmp          _prog
_take_count_right:
    ;если count_0 ==0 ,  то надо взять count_right
    load_addr    count_right
    store_addr   count_0


_prog:
    load_addr    count_0                     ;
    beqz         _a                          ;если пустая строка, ты надо вывести 00 и не возвращаться
    sub          one                         ; двигаем назад указатель, т.к. он указывает сейчас на следующий
    store_addr   count_0

    load_addr    count_0
    load_acc                                 ;0x5f5f5f6f
    and          o00f                        ; 0x0000006f
    store_addr   first_char                  ;взяли последний и сохранили только символ

    load_addr    count_left
    load_acc                                 ;0x6c6c6548
    and          o00f                        ;0x00000048
    store_addr   second_char                 ; взяли первый и сохранили только символ

    load_addr    count_left                  ;0x00000000
    load_acc                                 ;0x6c6c6548
    and          fff0                        ;0x6c6c6500
    or           first_char                  ;0x6c6c656f
    store_ind    count_left                  ; последний положили на первое место

    load_addr    count_0                     ;0x00000004
    load_acc                                 ;0x5f5f5f6f
    and          fff0                        ;0x5f5f5f00
    or           second_char                 ;0x5f5f5f48
    store_ind    count_0                     ; первый положили на последнее место

    load_addr    count_left
    add          one
    store_addr   count_left                  ; пододвинули вправо левый указатель

    sub          count_0                     ; хотим проверить, что левый указатель правее правого
    bgez         _output
    jmp          _prog


_output:
    load_imm     0x0                         ;
    store_addr   count_left                  ; начинаем с нулегого указателя
_outcycl:
    load_acc                                 ; загружаем значение в аккамулятор
    and          o00f                        ; берём только последние символы
    sub          o                           ; выставляем флаг
    beqz         _end                        ; если 00 конец, то завершаем
    store_ind    output                      ; выгружаем символ на выход
    load_addr    count_left
    add          one                         ;инкрементируем указатель
    store_addr   count_left
    jmp          _outcycl

_a:
    ; если пустая строка
    or           F5F5F500
    store_ind    count_0


_end:
    halt
_c:
    ; если больше 0x20 значений на ввод
    load_imm     0xcccccccc
    store_ind    output
    jmp          _end

_oo:
    ; если встретили в вводе 00 , то сохранили count_right в count_0, что бы потом разворачивать только до него
    load_addr    count_right
    store_addr   count_0
    load_imm     0x0
    jmp          _pause