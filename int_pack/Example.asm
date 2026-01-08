include "ISA.inc"
include "uio.inc"
include "math.inc"

entry main

main:
	; ccall print, .str addr  		; вывод считанной строки
	; mov r:1, .long_const
	; lds r:1, [r:1]
	ccall udiv, [.long_const], 0x19
 	; ccall _bsr, [.long_const]		; r:0 -  старший бит делителя
	hlt

.long_const dd 0xFAFFFDFF
.str db "Привет", 0
align 4

