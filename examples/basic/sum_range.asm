format binary

include "ISA.inc"


func_main:
	; Function: main
	mov r0, 1
	mov r26, r0
	mov r1, 10
	mov r27, r1
	mov r30, ret_addr_0
	mov r31, func_sum_range
ret_addr_0:
	mov r2, r0
	mov r11, r2
	mov r0, r11
	hlt

func_sum_range:
	; Function: sum_range
	mov r0, 0
	mov r13, r0
	mov r14, 0
	mov r14, r26
for_start_1:
	cmpa r2, r14, r27
	mov r3, 1
	mov r4, 0
	cmovz r1, r2, r3
	cmovnz r1, r2, r4
	mov r5, 0
	cmovz r31, r1, for_end_2
	add r6, r13, r14
	mov r13, r6
	mov r7, 1
	add r8, r14, r7
	mov r14, r8
	mov r31, for_start_1
for_end_2:
	mov r0, r13
	mov r31, r30