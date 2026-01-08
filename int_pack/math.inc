if used umul
	; r:1 - первый множитель, r:2 - второй множитель, r:0 - результат
	umul:
		mov r:0, 0
			cmovz r:31, r:2, .return addr
			cmovz r:31, r:1, .return addr
		; r:3   		; проверка выхода флага
		mov r:4, 1   	; флаг
		mov r:5, 1   	; сдвиг
		.loop:
			and r:6, r:2, r:4
			cmovz r:31, r:6, .no_add addr
				add r:0, r:0, r:1
			.no_add:
			shl r:4, r:4, r:5
			shl r:1, r:1, r:5
		cmovz r:31, r:4, .return addr
		cmpa r:3, r:4, r:2
		cmovz r:31, r:3, .loop addr
		.return: lds r:31, [r:30]
end if

if used _bsr
	; r:1 - источник, r:0 - результат, 0xFFFFFFFF - ошибка
	_bsr:
		mov r:0, 0
		cmovz r:31, r:1, .error addr
		cmpe r:2, r:1, 1
			cmovnz r:31, r:2, .return addr
		sub r:0, r:0, 1 ; счет от 0
		mov r:2, 1  	; флаг
		mov r:3, 1  	; сдвиг
		.loop:
			cmovz r:31, r:2, .return addr ; overflow
			shl r:2, r:2, r:3
			add r:0, r:0, 1
		cmpa r:4, r:2, r:1
		cmovz r:31, r:4, .loop addr 
		.return: lds r:31, [r:30]

		.error:
			not r:0, r:0
			lds r:31, [r:30]
end if

if used udiv
	; r:1 - делимое, r:2 - делитель, r:0 - частное, r:1 - остаток
	udiv:
		cmovz r:31, r:2, .error addr
		mov r:0, 0
		cmpa r:3, r:2, r:1
			cmovnz r:31, r:3, .return addr
		sub r:3, r:2, r:1
			cmovz r:31, r:3, .equal addr
	 	_push r:1
	 	_push r:2
	 	ccall _bsr, r:1
	 	lds r:1, [r:30]
	 	_push r:0      		; вершина стека - старший бит делимого
	 	ccall _bsr, r:1		; r:0 -  старший бит делителя
	 	mov r:4, r:0  		; r:4 - старший бит делителя
	 	_pop r:2  			; r:2 - старший бит делимого
	 	sub r:2, r:2, r:4  	; r:2 - разница между старшими битами
	 		cmovz r:31, r:2, .equal_max_bit addr
	 	_pop r:3  			; r:3 - делитель
	 	shl r:3, r:3, r:2   ; r:3 - сдвигаемый делитель
	 	_pop r:1  			; r:1 - делимое
	 	mov r:4, 1  		; r:4 - сдвиг
	 	mov r:0, 0
	 	.loop:
	 		shl r:0, r:0, r:4
	 		cmpa r:5, r:3, r:1
	 		cmovnz r:31, r:5, .no_add addr
	 			add r:0, r:0, 1
	 			sub r:1, r:1, r:3
	 		.no_add:
		 	shr r:3, r:3, r:4
		 	sub r:2, r:2, 1
	 		cmovz r:31, r:1, ._break addr
	 	cmpe r:5, r:2, 0
	 	cmovz r:31, r:5, .loop addr
	 	._break:
	 	add r:2, r:2, 1
		shl r:0, r:0, r:2
	 	.return: lds r:31, [r:30]

	 	.equal:
	 		mov r:0, 1
	 		mov r:1, 0
	 		lds r:31, [r:30]

	 	.equal_max_bit:
	 		add r:30, r:30, 2
	 		sub r:1, r:1, r:2
	 		mov r:0, 1
	 		lds r:31, [r:30]

	 	.error: hlt
end if
