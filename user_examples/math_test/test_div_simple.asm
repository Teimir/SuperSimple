;format binary

include "../../int_pack/ISA.inc"
include "../../int_pack/macros.inc"

entry main


main:
	; Function: main
	mov r:1, 115200
	mov r:3, 115200
	setu r:3
	mov r:2, 0
	mov r:4, 123
	mov r:11, r:4
	mov r:26, r:11
	mov r:5, 10
	mov r:27, r:5
	mov r:30, ret_addr_0 addr
	mov r:31, func_umod addr
ret_addr_0:
	mov r:6, r:0
	mov r:12, r:6
	mov r:7, 48
	add r:8, r:7, r:12
	outu r:8
	mov r:9, 0
	mov r:0, r:9
	hlt

func_udiv:
	; Function: udiv
	mov r:1, r:30
	sub r:30, r:30, 1
	lds [r:30], r:1
	mov r:2, 0
	cmpe r:3, r:27, r:2
	mov r:4, -1
	cmovz r:3, r:3, r:4
	xor r:3, r:3, r:4
	mov r:5, 0
	cmovz r:31, r:3, endif_2 addr
	mov r:6, 0
	mov r:0, r:6
	lds r:29, [r:30]
	add r:30, r:30, 1
	mov r:31, r:29
endif_2:
	cmpb r:7, r:26, r:27
	mov r:8, -1
	cmovz r:7, r:7, r:8
	xor r:7, r:7, r:8
	mov r:9, 0
	cmovz r:31, r:7, endif_4 addr
	mov r:1, 0
	mov r:0, r:1
	lds r:29, [r:30]
	add r:30, r:30, 1
	mov r:31, r:29
endif_4:
	mov r:1, 1
	cmpe r:2, r:27, r:1
	mov r:3, -1
	cmovz r:2, r:2, r:3
	xor r:2, r:2, r:3
	mov r:4, 0
	cmovz r:31, r:2, endif_6 addr
	mov r:0, r:26
	lds r:29, [r:30]
	add r:30, r:30, 1
	mov r:31, r:29
endif_6:
	mov r:5, 0
	mov r:13, r:5
	mov r:14, r:26
	mov r:15, r:27
	mov r:6, 0
	mov r:16, r:6
while_start_7:
	cmpa r:8, r:15, r:14
	mov r:9, 1
	mov r:1, 0
	cmovz r:7, r:8, r:9
	cmovnz r:7, r:8, r:1
	mov r:1, 32
	cmpb r:2, r:16, r:1
	mov r:3, -1
	cmovz r:2, r:2, r:3
	xor r:2, r:2, r:3
	mov r:5, 0
	mov r:6, 1
	cmpe r:8, r:7, r:5
	cmpe r:9, r:2, r:5
	cmpe r:1, r:8, r:5
	cmpe r:3, r:9, r:5
	mov r:4, 0
	cmovz r:4, r:1, r:6
	cmovnz r:4, r:3, r:5
	mov r:10, 0
	cmovz r:31, r:4, while_end_8 addr
	mov r:4, 1
	shl r:5, r:15, r:4
	mov r:15, r:5
	mov r:6, 1
	add r:7, r:16, r:6
	mov r:16, r:7
	mov r:31, while_start_7 addr
while_end_8:
	mov r:8, 0
	cmpa r:9, r:16, r:8
	mov r:1, -1
	cmovz r:9, r:9, r:1
	xor r:9, r:9, r:1
	mov r:1, 0
	cmovz r:31, r:9, endif_10 addr
	mov r:2, 1
	sub r:3, r:16, r:2
	mov r:16, r:3
	mov r:4, 1
	shr r:5, r:15, r:4
	mov r:15, r:5
endif_10:
	mov r:6, 1
	mov r:17, r:6
while_start_11:
	mov r:7, 0
	cmpe r:8, r:17, r:7
	mov r:9, -1
	cmovnz r:8, r:8, r:9
	xor r:8, r:8, r:9
	cmpb r:1, r:14, r:27
	mov r:2, 1
	mov r:3, 0
	cmovz r:1, r:1, r:3
	cmovnz r:1, r:1, r:2
	mov r:5, 0
	mov r:6, 1
	cmpe r:7, r:8, r:5
	cmpe r:9, r:1, r:5
	cmpe r:2, r:7, r:5
	cmpe r:3, r:9, r:5
	mov r:4, 0
	cmovz r:4, r:2, r:6
	cmovnz r:4, r:3, r:5
	mov r:10, 0
	cmovz r:31, r:4, while_end_12 addr
	cmpb r:5, r:14, r:15
	mov r:6, 1
	mov r:7, 0
	cmovz r:4, r:5, r:7
	cmovnz r:4, r:5, r:6
	mov r:8, 0
	cmovz r:31, r:4, endif_14 addr
	sub r:9, r:14, r:15
	mov r:14, r:9
	mov r:1, 1
	shl r:1, r:1, r:16
	add r:2, r:13, r:1
	mov r:13, r:2
endif_14:
	mov r:3, 1
	shr r:4, r:15, r:3
	mov r:15, r:4
	mov r:5, 0
	cmpa r:6, r:16, r:5
	mov r:7, -1
	cmovz r:6, r:6, r:7
	xor r:6, r:6, r:7
	mov r:8, 0
	cmovz r:31, r:6, else_15 addr
	mov r:9, 1
	sub r:1, r:16, r:9
	mov r:16, r:1
	mov r:31, endif_16 addr
else_15:
	mov r:1, 0
	mov r:17, r:1
endif_16:
	mov r:31, while_start_11 addr
while_end_12:
	mov r:0, r:13
	lds r:29, [r:30]
	add r:30, r:30, 1
	mov r:31, r:29

func_umod:
	; Function: umod
	mov r:1, r:30
	sub r:30, r:30, 1
	lds [r:30], r:1
	mov r:2, 0
	cmpe r:3, r:27, r:2
	mov r:4, -1
	cmovz r:3, r:3, r:4
	xor r:3, r:3, r:4
	mov r:5, 0
	cmovz r:31, r:3, endif_18 addr
	mov r:6, 0
	mov r:0, r:6
	lds r:29, [r:30]
	add r:30, r:30, 1
	mov r:31, r:29
endif_18:
	cmpb r:7, r:26, r:27
	mov r:8, -1
	cmovz r:7, r:7, r:8
	xor r:7, r:7, r:8
	mov r:9, 0
	cmovz r:31, r:7, endif_20 addr
	mov r:0, r:26
	lds r:29, [r:30]
	add r:30, r:30, 1
	mov r:31, r:29
endif_20:
	mov r:1, 1
	cmpe r:2, r:27, r:1
	mov r:3, -1
	cmovz r:1, r:2, r:3
	xor r:1, r:1, r:3
	mov r:4, 0
	cmovz r:31, r:1, endif_22 addr
	mov r:5, 0
	mov r:0, r:5
	lds r:29, [r:30]
	add r:30, r:30, 1
	mov r:31, r:29
endif_22:
	mov r:13, r:26
	mov r:14, r:27
	mov r:6, 0
	mov r:15, r:6
while_start_23:
	cmpa r:8, r:14, r:13
	mov r:9, 1
	mov r:1, 0
	cmovz r:7, r:8, r:9
	cmovnz r:7, r:8, r:1
	mov r:1, 32
	cmpb r:2, r:15, r:1
	mov r:3, -1
	cmovz r:2, r:2, r:3
	xor r:2, r:2, r:3
	mov r:5, 0
	mov r:6, 1
	cmpe r:8, r:7, r:5
	cmpe r:9, r:2, r:5
	cmpe r:1, r:8, r:5
	cmpe r:3, r:9, r:5
	mov r:4, 0
	cmovz r:4, r:1, r:6
	cmovnz r:4, r:3, r:5
	mov r:10, 0
	cmovz r:31, r:4, while_end_24 addr
	mov r:4, 1
	shl r:5, r:14, r:4
	mov r:14, r:5
	mov r:6, 1
	add r:7, r:15, r:6
	mov r:15, r:7
	mov r:31, while_start_23 addr
while_end_24:
	mov r:8, 0
	cmpa r:9, r:15, r:8
	mov r:1, -1
	cmovz r:9, r:9, r:1
	xor r:9, r:9, r:1
	mov r:1, 0
	cmovz r:31, r:9, endif_26 addr
	mov r:2, 1
	sub r:3, r:15, r:2
	mov r:15, r:3
	mov r:4, 1
	shr r:5, r:14, r:4
	mov r:14, r:5
endif_26:
	mov r:6, 1
	mov r:16, r:6
while_start_27:
	mov r:7, 0
	cmpe r:8, r:16, r:7
	mov r:9, -1
	cmovnz r:8, r:8, r:9
	xor r:8, r:8, r:9
	cmpb r:1, r:13, r:27
	mov r:2, 1
	mov r:3, 0
	cmovz r:1, r:1, r:3
	cmovnz r:1, r:1, r:2
	mov r:5, 0
	mov r:6, 1
	cmpe r:7, r:8, r:5
	cmpe r:9, r:1, r:5
	cmpe r:2, r:7, r:5
	cmpe r:3, r:9, r:5
	mov r:4, 0
	cmovz r:4, r:2, r:6
	cmovnz r:4, r:3, r:5
	mov r:10, 0
	cmovz r:31, r:4, while_end_28 addr
	cmpb r:5, r:13, r:14
	mov r:6, 1
	mov r:7, 0
	cmovz r:4, r:5, r:7
	cmovnz r:4, r:5, r:6
	mov r:8, 0
	cmovz r:31, r:4, endif_30 addr
	sub r:9, r:13, r:14
	mov r:13, r:9
endif_30:
	mov r:1, 1
	shr r:1, r:14, r:1
	mov r:14, r:1
	mov r:2, 0
	cmpa r:3, r:15, r:2
	mov r:4, -1
	cmovz r:3, r:3, r:4
	xor r:3, r:3, r:4
	mov r:5, 0
	cmovz r:31, r:3, else_31 addr
	mov r:6, 1
	sub r:7, r:15, r:6
	mov r:15, r:7
	mov r:31, endif_32 addr
else_31:
	mov r:8, 0
	mov r:16, r:8
endif_32:
	mov r:31, while_start_27 addr
while_end_28:
	mov r:0, r:13
	lds r:29, [r:30]
	add r:30, r:30, 1
	mov r:31, r:29

func_sdiv:
	; Function: sdiv
	mov r:1, r:30
	sub r:30, r:30, 1
	lds [r:30], r:1
	mov r:2, 0
	cmpe r:3, r:27, r:2
	mov r:4, -1
	cmovz r:3, r:3, r:4
	xor r:3, r:3, r:4
	mov r:5, 0
	cmovz r:31, r:3, endif_34 addr
	mov r:6, 0
	mov r:0, r:6
	lds r:29, [r:30]
	add r:30, r:30, 1
	mov r:31, r:29
endif_34:
	mov r:7, 0
	mov r:13, r:7
	mov r:8, 0
	mov r:14, r:8
	mov r:15, r:26
	mov r:16, r:27
	mov r:9, 2147483648
	and r:1, r:26, r:9
	mov r:17, r:1
	mov r:1, 0
	cmpe r:2, r:17, r:1
	mov r:3, -1
	cmovnz r:2, r:2, r:3
	xor r:2, r:2, r:3
	mov r:4, 0
	cmovz r:31, r:2, endif_36 addr
	mov r:5, 1
	mov r:13, r:5
	mov r:7, 0
	sub r:6, r:7, r:26
	mov r:15, r:6
endif_36:
	mov r:8, 2147483648
	and r:9, r:27, r:8
	mov r:17, r:9
	mov r:1, 0
	cmpe r:2, r:17, r:1
	mov r:3, -1
	cmovnz r:1, r:2, r:3
	xor r:1, r:1, r:3
	mov r:4, 0
	cmovz r:31, r:1, endif_38 addr
	mov r:5, 1
	mov r:14, r:5
	mov r:7, 0
	sub r:6, r:7, r:27
	mov r:16, r:6
endif_38:
	mov r:26, r:15
	mov r:27, r:16
	mov r:30, ret_addr_39 addr
	mov r:31, func_udiv addr
ret_addr_39:
	mov r:8, r:0
	mov r:18, r:8
	cmpe r:9, r:13, r:14
	mov r:1, -1
	cmovnz r:9, r:9, r:1
	xor r:9, r:9, r:1
	mov r:1, 0
	cmovz r:31, r:9, endif_41 addr
	mov r:3, 0
	sub r:2, r:3, r:18
	mov r:18, r:2
endif_41:
	mov r:0, r:18
	lds r:29, [r:30]
	add r:30, r:30, 1
	mov r:31, r:29

func_smod:
	; Function: smod
	mov r:1, r:30
	sub r:30, r:30, 1
	lds [r:30], r:1
	mov r:2, 0
	cmpe r:3, r:27, r:2
	mov r:4, -1
	cmovz r:3, r:3, r:4
	xor r:3, r:3, r:4
	mov r:5, 0
	cmovz r:31, r:3, endif_43 addr
	mov r:6, 0
	mov r:0, r:6
	lds r:29, [r:30]
	add r:30, r:30, 1
	mov r:31, r:29
endif_43:
	mov r:7, 0
	mov r:13, r:7
	mov r:14, r:26
	mov r:15, r:27
	mov r:8, 2147483648
	and r:9, r:26, r:8
	mov r:16, r:9
	mov r:1, 0
	cmpe r:2, r:16, r:1
	mov r:3, -1
	cmovnz r:1, r:2, r:3
	xor r:1, r:1, r:3
	mov r:4, 0
	cmovz r:31, r:1, endif_45 addr
	mov r:5, 1
	mov r:13, r:5
	mov r:7, 0
	sub r:6, r:7, r:26
	mov r:14, r:6
endif_45:
	mov r:8, 2147483648
	and r:9, r:27, r:8
	mov r:16, r:9
	mov r:1, 0
	cmpe r:2, r:16, r:1
	mov r:3, -1
	cmovnz r:1, r:2, r:3
	xor r:1, r:1, r:3
	mov r:4, 0
	cmovz r:31, r:1, endif_47 addr
	mov r:6, 0
	sub r:5, r:6, r:27
	mov r:15, r:5
endif_47:
	mov r:26, r:14
	mov r:27, r:15
	mov r:30, ret_addr_48 addr
	mov r:31, func_umod addr
ret_addr_48:
	mov r:7, r:0
	mov r:17, r:7
	mov r:8, 0
	cmovz r:31, r:13, endif_50 addr
	mov r:1, 0
	sub r:9, r:1, r:17
	mov r:17, r:9
endif_50:
	mov r:0, r:17
	lds r:29, [r:30]
	add r:30, r:30, 1
	mov r:31, r:29

func_udiv_fast:
	; Function: udiv_fast
	mov r:1, r:30
	sub r:30, r:30, 1
	lds [r:30], r:1
	mov r:2, 0
	cmpe r:3, r:27, r:2
	mov r:4, -1
	cmovz r:3, r:3, r:4
	xor r:3, r:3, r:4
	mov r:5, 0
	cmovz r:31, r:3, endif_52 addr
	mov r:6, 0
	mov r:0, r:6
	lds r:29, [r:30]
	add r:30, r:30, 1
	mov r:31, r:29
endif_52:
	mov r:7, 1
	sub r:8, r:27, r:7
	mov r:13, r:8
	and r:9, r:27, r:13
	mov r:1, 0
	cmpe r:2, r:9, r:1
	mov r:3, -1
	cmovz r:1, r:2, r:3
	xor r:1, r:1, r:3
	mov r:4, 0
	cmovz r:31, r:1, endif_54 addr
	mov r:5, 0
	mov r:14, r:5
	mov r:15, r:27
while_start_55:
	mov r:6, 1
	cmpa r:7, r:15, r:6
	mov r:8, -1
	cmovz r:7, r:7, r:8
	xor r:7, r:7, r:8
	mov r:10, 0
	cmovz r:31, r:7, while_end_56 addr
	mov r:9, 1
	shr r:1, r:15, r:9
	mov r:15, r:1
	mov r:1, 1
	add r:2, r:14, r:1
	mov r:14, r:2
	mov r:31, while_start_55 addr
while_end_56:
	shr r:3, r:26, r:14
	mov r:0, r:3
	lds r:29, [r:30]
	add r:30, r:30, 1
	mov r:31, r:29
endif_54:
	mov r:30, ret_addr_57 addr
	mov r:31, func_udiv addr
ret_addr_57:
	mov r:4, r:0
	mov r:0, r:4
	lds r:29, [r:30]
	add r:30, r:30, 1
	mov r:31, r:29

func_umod_fast:
	; Function: umod_fast
	mov r:1, r:30
	sub r:30, r:30, 1
	lds [r:30], r:1
	mov r:2, 0
	cmpe r:3, r:27, r:2
	mov r:4, -1
	cmovz r:3, r:3, r:4
	xor r:3, r:3, r:4
	mov r:5, 0
	cmovz r:31, r:3, endif_59 addr
	mov r:6, 0
	mov r:0, r:6
	lds r:29, [r:30]
	add r:30, r:30, 1
	mov r:31, r:29
endif_59:
	mov r:7, 1
	sub r:8, r:27, r:7
	mov r:13, r:8
	and r:9, r:27, r:13
	mov r:1, 0
	cmpe r:2, r:9, r:1
	mov r:3, -1
	cmovz r:1, r:2, r:3
	xor r:1, r:1, r:3
	mov r:4, 0
	cmovz r:31, r:1, endif_61 addr
	and r:5, r:26, r:13
	mov r:0, r:5
	lds r:29, [r:30]
	add r:30, r:30, 1
	mov r:31, r:29
endif_61:
	mov r:30, ret_addr_62 addr
	mov r:31, func_umod addr
ret_addr_62:
	mov r:6, r:0
	mov r:0, r:6
	lds r:29, [r:30]
	add r:30, r:30, 1
	mov r:31, r:29