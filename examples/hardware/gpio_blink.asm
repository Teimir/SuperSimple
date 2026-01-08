include "../../int_pack/ISA.inc"


func_main:
	; Function: main
	mov r1, 0
	mov r2, 1
	mov r3, 2
	shl r4, r1, 16
	shl r5, r2, 8
	or r4, r4, r5
	or r4, r4, r3
	setg r4
	mov r0, 0
	mov r11, 0
	mov r6, 0
	mov r11, r6
for_start_0:
	mov r7, 10
	cmpb r8, r11, r7
	mov r9, -1
	cmovz r8, r8, r9
	xor r8, r8, r9
	mov r10, 0
	cmovz r31, r8, addr for_end_1
	mov r1, 0
	mov r2, 1
	shl r3, r1, 8
	or r3, r3, r2
	outg r3
	mov r0, 0
	mov r5, 0
	mov r6, 0
	shl r7, r5, 8
	or r7, r7, r6
	outg r7
	mov r4, 0
	mov r8, 1
	add r11, r11, r8
	mov r31, addr for_start_0
for_end_1:
	mov r9, 0
	mov r0, r9
	hlt