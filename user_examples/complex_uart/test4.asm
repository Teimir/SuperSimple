;format binary

include "../../int_pack/ISA.inc"
include "../../int_pack/macros.inc"

entry main


main:
	; Function: main
	mov r:0, 65
	mov r:11, r:0
for_start_0:
	mov r:1, 127
	cmpb r:2, r:11, r:1
	mov r:3, -1
	cmovz r:2, r:2, r:3
	xor r:2, r:2, r:3
	mov r:4, 0
	cmovz r:31, r:2, for_end_1 addr
	outu r:11
	mov r:5, 1
	add r:11, r:11, r:5
	mov r:31, for_start_0 addr
for_end_1:
	mov r:6, 0
	mov r:0, r:6
	hlt