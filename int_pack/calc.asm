;format binary

include "ISA.inc"
entry main



main:
inu r:0
getu r:2
outu r:2
; --- Стартовая метка ---
.start:
  getu r:2
  mov r:3, 0FFh
  and r:2, r:2, r:3
  mov r:3, 01h
  cmpb r:2, r:2, r:3
  cmovnz r:31, r:2, .start addr
  inu r:0
  outu r:0
  ; --- Выход из программы ---
  mov r:1, exits addr
  lds r:1, [r:1]
  cmpe r:1, r:0, r:1  
  mov r:2, .stop addr
  cmovnz r:31, r:1, r:2
  ; --- Сложение ---
  mov r:1, pluss addr
  lds r:1, [r:1]
  cmpe r:1, r:0, r:1  
  mov r:2, .plus addr
  cmovnz r:31, r:1, r:2
  ; --- Вычитание
  mov r:1, minuss addr
  lds r:1, [r:1]
  cmpe r:1, r:0, r:1  
  mov r:2, .minus addr
  cmovnz r:31, r:1, r:2
  ; --- Умножение
  mov r:1, multipl addr
  lds r:1, [r:1]
  cmpe r:1, r:0, r:1  
  mov r:2, .multiply addr
  cmovnz r:31, r:1, r:2
  ; --- Деление
  mov r:1, divd addr
  lds r:1, [r:1]
  cmpe r:1, r:0, r:1  
  mov r:2, .divide addr
  cmovnz r:31, r:1, r:2
  ; --- Если команда неправильная --- 
  mov r:31, .start addr


; ------- Функция сложения
.plus:
  ; --- Получение цифр
  getu r:2
  mov r:3, 0FFh
  and r:2, r:2, r:3
  mov r:3, 02h
  cmpb r:2, r:2, r:3
  cmovnz r:31, r:2, .plus addr
  ; --- Вычисление
  mov r:0, 00h
  mov r:1, 00h
  inu r:0
  outu r:0
  inu r:1
  outu r:1
  add r:1, r:1, r:0
  outu r:1
  mov r:31, .start addr


; ------- Функция вычитания
.minus:
  ; --- Получение цифр
  getu r:2
  mov r:3, 0FFh
  and r:2, r:2, r:3
  mov r:3, 02h
  cmpb r:2, r:2, r:3
  cmovnz r:31, r:2, .minus addr
  ; --- Вычисление
  mov r:0, 00h
  mov r:1, 00h
  inu r:0
  outu r:0
  inu r:1
  outu r:1
  sub r:1, r:0, r:1
  outu r:1
  mov r:31, .start addr

; ------- Функция умножения
.multiply:
  ; --- Получение цифр
  getu r:2
  mov r:3, 0FFh
  and r:2, r:2, r:3
  mov r:3, 02h
  cmpb r:2, r:2, r:3
  cmovnz r:31, r:2, .multiply addr
  mov r:2, 00h
  mov r:4, 00h
  inu r:2
  outu r:2
  inu r:4
  outu r:4
  add r:30, r:31, 01h
  mov r:31, .mul addr
  outu r:1
  mov r:31, .start addr


; ------- Функция деления
.divide:
  ; --- Получение цифр
  getu r:2
  mov r:3, 0FFh
  and r:2, r:2, r:3
  mov r:3, 02h
  cmpb r:2, r:2, r:3
  cmovnz r:31, r:2, .divide addr
  mov r:2, 00h
  mov r:4, 00h
  inu r:2
  outu r:2
  inu r:4
  outu r:4
  add r:30, r:31, 01h
  mov r:31, .div addr
  outu r:1
  outu r:2
  mov r:31, .start addr

; ------- Функция остановки
.stop:
  outu r:31
  hlt

; -- Умножение
; r:1 - return
; r:30 - ret addr
; r:2 - a, r:4 - b, r:3 in use
.mul:
  mov r:1, 00h
  cmpb r:3, r:2, r:4
  cmovz r:31, r:3, .mul_m1 addr
  mov r:3, r:2
  mov r:2, r:4
  mov r:4, r:3
  .mul_m1:
    add r:1, r:2, r:1
    sub r:4, r:4, 01h
    cmovz r:31, r:4, .mul_nd addr
    mov r:31, .mul_m1 addr
  .mul_nd:
  mov r:31, r:30

; -- Деление
; r:1 целая часть
; r:2 дробная часть
; r:2 делимое 
; r:4 делитель
; r:30 - ret addr
.div: 
  mov r:1, 00h
.div_m1:
    cmpb r:3, r:2, r:4
    cmovnz r:31, r:3, .div_nd addr
    sub r:2, r:2, r:4 
    add r:1, r:1, 01h
    mov r:31, .div_m1 addr
.div_nd:
  mov r:31, r:30

; --- Строку в число
; r:1 число
; r:2, r:4, r:3 in use
; r:30 - ret addr
.strtonum:
  ; --- Получение цифр
  mov r:1, 00h
  .strtonum_loop:
  ; -- Проверка наличия байта в юарте
  getu r:2
  mov r:3, 0FFh
  and r:2, r:2, r:3
  mov r:3, 01h
  cmpb r:2, r:2, r:3
  cmovnz r:31, r:2, .strtonum_loop addr
  ; --  Если есть байт, то проверяем цифра ли это
  getu r:2
  mov r:3, uartdatalookup addr
  lds r:3, [r:3]
  and r:2, r:2, r:3
  shr r:2, r:2, 10h
  ; ЕСЛИ Байт с юарта больше 2Ф и меньше 3А,
  ; тогда он принадлежит ["0";"9"]
  cmpa r:3, r:2, 2Fh ;"0" - 1
  cmpb r:4, r:2, 3Ah ;"9" + 1
  and r:3, r:3, r:4 
  cmovz r:31, r:3, r:30
  ; -- Сохраняем адрес возврата
  mov r:4, strtonumret addr
  lds [r:4], r:30
  ; -- Умножаем
    mov r:2, r:1
    mov r:4, 0Ah
    add r:30, r:31, 01h
    mov r:31, .mul addr
  ; -- Возвращаем адрес возврата
  mov r:4, strtonumret addr
  lds r:30, [r:4]
  ; -- Сохраняем последнее число и добавляем в регистр
  inu r:4
  sub r:4, r:4, 1Eh
  add r:1, r:1, r:4
  ; -- Переходим в начало цикла
  mov r:31, .strtonum_loop addr


  

; ------ Данные
hlt
exits dd 021h
pluss dd 02Bh
minuss dd 02Dh
multipl dd 02Ah
divd dd 02fh
uartdatalookup dd 0FF0000h
strtonumret dd 00h
