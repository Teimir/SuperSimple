;format binary

include "../../../int_pack/ISA.inc"
include "../../../int_pack/macros.inc"

entry main


main:
	; Function: main
	mov r:0, 72
	outu r:0
	mov r:1, 101
	outu r:1
	mov r:2, 108
	outu r:2
	mov r:3, 108
	outu r:3
	mov r:4, 111
	outu r:4
	mov r:5, 32
	outu r:5
	mov r:6, 87
	outu r:6
	mov r:7, 111
	outu r:7
	mov r:8, 114
	outu r:8
	mov r:9, 108
	outu r:9
	mov r:10, 100
	outu r:10
	mov r:0, 0
	hlt