;format binary

include "../../int_pack/ISA.inc"
include "../../int_pack/macros.inc"

entry main


main:
	; Function: main
	; Allocate array arr1[9] on stack
	sub r:30, r:30, 9
	mov r:0, 66
	mov r:1, r:30
	lds [r:1], r:0
	mov r:2, 121
	mov r:3, r:30
	mov r:4, 1
	add r:3, r:3, r:4
	lds [r:3], r:2
	mov r:5, 101
	mov r:6, r:30
	mov r:7, 2
	add r:6, r:6, r:7
	lds [r:6], r:5
	mov r:8, 32
	mov r:9, r:30
	mov r:10, 3
	add r:9, r:9, r:10
	lds [r:9], r:8
	mov r:0, 87
	mov r:1, r:30
	mov r:2, 4
	add r:1, r:1, r:2
	lds [r:1], r:0
	mov r:3, 111
	mov r:4, r:30
	mov r:5, 5
	add r:4, r:4, r:5
	lds [r:4], r:3
	mov r:6, 114
	mov r:7, r:30
	mov r:8, 6
	add r:7, r:7, r:8
	lds [r:7], r:6
	mov r:9, 108
	mov r:10, r:30
	mov r:0, 7
	add r:10, r:10, r:0
	lds [r:10], r:9
	mov r:1, 100
	mov r:2, r:30
	mov r:3, 8
	add r:2, r:2, r:3
	lds [r:2], r:1
	mov r:4, 0
	mov r:11, r:4
for_start_0:
	mov r:5, 9
	cmpb r:6, r:11, r:5
	mov r:7, -1
	cmovz r:6, r:6, r:7
	xor r:6, r:6, r:7
	mov r:8, 0
	cmovz r:31, r:6, for_end_1 addr
	mov r:10, r:30
	add r:10, r:10, r:11
	lds r:9, [r:10]
	outu r:9
	mov r:0, 1
	add r:11, r:11, r:0
	mov r:31, for_start_0 addr
for_end_1:
	mov r:1, 0
	mov r:0, r:1
	hlt