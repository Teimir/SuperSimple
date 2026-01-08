format binary

; вспомогательный макрос для того, чтобы собирать 
; из операндов опкоды
; схема такая:
; биты 0-2 - тип команды
; биты 3-6 - операция
; биты 7-11 - первый операнд-регистр
; типы команд:
;	000b - nop
; 	001b - регистр, литерал
; 		биты 12-31 - длинный литерал(20 бит)
; 	010b - регистр, регистр, литерал
;		биты 12-16 - второй операнд-регистр
;		биты 17-31 - короткий литерал(15 бит)
; 	011b - регистр, регистр, регистр
;		биты 12-16 - второй операнд-регистр
;		биты 17-21 - третий операнд-регистр
; 	110b - регистр, регистр, регистр, регистр(и все инструкции сдвигов)
;		биты 12-16 - второй операнд-регистр
;		биты 17-21 - третий операнд-регистр
;		биты 22-26 - четвертый операнд-регистр

macro _instr opcode, instrnum*, op1*, op2=r:0, op3=r:0, op4{
	opcode = (instrnum and 1111b) shl 3  								; операция
	match =r:reg1, op1\{
		opcode = opcode or ((reg1 and 11111b) shl 7)
		match =r:reg2, op2\\{											; если второй операнд регистр
			opcode = opcode or ((reg2 and 11111b) shl 12)
			match =r:reg3, op3\\\{										; если третий операнд регистр
				opcode = opcode or ((reg3 and 11111b) shl 17)
				match =r:reg4, op4\\\\{									; если 4 аргумент есть и он регистр
					opcode = opcode or ((reg4 and 11111b) shl 22)
					opcode = opcode or 110b
				rept 0\\\\{\\\\} rept 1\\\\{ 							; если 4 аргумент не регистр(считается что его нет)
					opcode = opcode or 011b
				\\\\}
			rept 0\\\{\\\} rept 1\\\{ 									; если 3-й аргумент не регистр
				opcode = opcode or ((op3 and 111111111111111b) shl 17)	; значит короткий литерал ()
				opcode = opcode or 010b
			\\\}
		rept 0\\{\\} rept 1\\{ 											; если второй операнд не регистр
			opcode = opcode or ((op2 and 11111111111111111111b) shl 12)	; значит длинный литерал
			opcode = opcode or 001b
		\\}
	\}
}

nop equ dd 0

hlt equ dd 5

macro mov args*&{
	local opcode
	_instr opcode, 0, args
	dd opcode
}

macro add args*&{
	local opcode
	_instr opcode, 1, args
	dd opcode
}

macro sub args*&{
	local opcode
	_instr opcode, 2, args
	dd opcode
}

macro not args*&{
	local opcode
	_instr opcode, 3, args
	dd opcode
}

macro and args*&{
	local opcode
	_instr opcode, 4, args
	dd opcode
}

macro or args*&{
	local opcode
	_instr opcode, 5, args
	dd opcode
}

macro xor args*&{
	local opcode
	_instr opcode, 6, args
	dd opcode
}

macro cmpa args*&{
	local opcode
	_instr opcode, 9, args
	dd opcode
}

macro cmpe args*&{
	local opcode
	_instr opcode, 10, args
	dd opcode
}

macro cmpb args*&{
	local opcode
	_instr opcode, 11, args
	dd opcode
}

macro cmovnz args*&{
	local opcode
	_instr opcode, 12, args
	dd opcode
}

macro cmovz args*&{
	local opcode
	_instr opcode, 13, args
	dd opcode
}

; для сдвиговых команд биты 30-31 определяют тип сдвига
macro shr args*&{
	local opcode
	_instr opcode, 7, args, r:0
	dd opcode
}

macro shl args*&{
	local opcode
	_instr opcode, 8, args, r:0
	dd opcode
}

macro sar args*&{
	local opcode
	_instr opcode, 7, args, r:0
	dd opcode or (1 shl 30)
}

macro sal args*&{
	local opcode
	_instr opcode, 8, args, r:0
	dd opcode or (1 shl 30)
}

macro shrd args*&{
	local opcode
	_instr opcode, 7, args
	dd opcode or (2 shl 30)
}

macro shld args*&{
	local opcode
	_instr opcode, 8, args
	dd opcode or (2 shl 30)
}

macro ror args*&{
	local opcode
	_instr opcode, 7, args, r:0
	dd opcode or (3 shl 30)
}

macro rol args*&{
	local opcode
	_instr opcode, 8, args, r:0
	dd opcode or (3 shl 30)
}

addr fix shr 2

; для работы с переферией вроде памяти и портов опкоды строятся немного иначе
; биты 0-2 - тип команды, 100b
; биты 3-4 - операция
; биты 5-6 - тип внешнего устройства:
_MEM_ 	= 00b 	; память
_UART_ 	= 01b 	; uart
_GPIO_ 	= 10b 	; порты
; биты 7-11 - первый операнд-регистр
; биты 12-16 - второй операнд-регистр 
macro _mug_ins opcode, _operation_, _out_, op1*, op2{
	opcode = 100b
	opcode = opcode or _operation_ shl 3
	opcode = opcode or _out_ shl 5
	match r:reg1, op1\{
		opcode = opcode or ((reg1 and 11111b) shl 7)
	\}
	match r:reg2, op2\{
		opcode = opcode or ((reg2 and 11111b) shl 12)
	\}
}

macro inm op1*, op2*{
	local opcode
	_mug_ins opcode, 0, _MEM_, op1, op2
	dd opcode
}

macro outm op1*, op2*{
	local opcode
	_mug_ins opcode, 1, _MEM_, op1, op2
	dd opcode
}

macro getu op1*{
	local opcode
	_mug_ins opcode, 0, _UART_, op1
	dd opcode
}

macro setu op1*{
	local opcode
	_mug_ins opcode, 1, _UART_, op1
	dd opcode
}

macro inu op1*{
	local opcode
	_mug_ins opcode, 10b, _UART_, op1
	dd opcode
}

macro outu op1*{
	local opcode
	_mug_ins opcode, 11b, _UART_, op1
	dd opcode
}

macro getg op1*{
	local opcode
	_mug_ins opcode, 0, _GPIO_, op1
	dd opcode
}

macro setg op1*{
	local opcode
	_mug_ins opcode, 1, _GPIO_, op1
	dd opcode
}

macro ing op1*{
	local opcode
	_mug_ins opcode, 10b, _GPIO_, op1
	dd opcode
}

macro outg op1*{
	local opcode
	_mug_ins opcode, 11b, _GPIO_, op1
	dd opcode
}

_start_code:

include "macros.inc"

; вспомогательный макрос для перевода числа в ascii-формат
macro dword_to_uint argum{
	local temp_val, divisor
	temp_val = argum
	divisor = 1
	while (divisor * 10) <= temp_val
		divisor = divisor * 10
	end while
	while divisor > 0
		db (temp_val / divisor)+30h
		temp_val = temp_val mod divisor
		divisor = divisor / 10
	end while
}

; создание mif-файла в конце компиляции
postpone{
	local dword_now, _main, dwords_count
	_end_code:
	virtual at 0 as "mif"
		_main::
		db "-- Quartus Prime generated Memory Initialization File(.mif)", 0Ah
		db 0Ah
		db "WIDTH = 32;", 0Ah
		db "DEPTH = 4096;", 0Ah
		db 0Ah
		db "ADDRESS_RADIX = UNS;", 0Ah
		db "DATA_RADIX = UNS;", 0Ah
		db 0Ah
		db "CONTENT BEGIN", 0Ah
	end virtual
	dwords_count = ((_end_code-_start_code) shr 2)		;количество двойных слов, каждое надо перевести в строку
	repeat dwords_count
		load dword_now dword from _start_code+(%-1)*4  	;загружаем текущий dword из бинарника
		virtual _main									;дописываем в mif
			db 09h										;табуляция для отступа
			dword_to_uint %-1							;номер dword`а
			db ": "
			dword_to_uint dword_now						;значение в десятичном беззнаковом ascii
			db ";", 0Ah 								;завершение строки и перенос
		end virtual
	end repeat
	if dwords_count < 4096								;если двордов меньше максимума, то добавляем строку
		virtual _main									;с занулением всех остальных
			db 09h, "["
			dword_to_uint dwords_count
			db "..4096]:0;", 0Ah 
		end virtual
	end if
	virtual _main
		db "END;"
	end virtual
}