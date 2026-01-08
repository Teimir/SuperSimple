if used print
	; r:1 - source c-string
	; r:1-r:5 registers used
	print:
		lds r:5, [r:30]
		mov r:2, 8
		.print_loop:
			lds r:0, [r:1]
			mov r:4, 4
			.dword_chars:
				outu r:0
				and r:3, r:0, 0FFh
					cmovz r:31, r:3, r:5
				shr r:0, r:0, r:2
				sub r:4, r:4, 1
			cmovz r:31, r:4, ._end_dword_chars addr
			mov r:31, .dword_chars addr
			._end_dword_chars:
			add r:1, r:1, 1
		mov r:31, .print_loop addr
end if


if used input
	; r:1 - destination c-string
	; r:2 - maximum data length(0-terminator not included)
	; r:0-r:7 regisers used
	input:
		mov r:3, 8
		mov r:0, 0
		mov r:5, r:0
		.read_loop:
			mov r:6, 4
			.read_dword:
				.wait_get:
					getu r:4
					and r:4, r:4, 0xFF
				cmovz r:31, r:4, .wait_get addr
				inu r:4
				and r:4, r:4, 0xFF
				cmpe r:7, r:4, 0xd
					cmovnz r:31, r:7, .return addr
				cmpe r:7, r:4, 0xa
					cmovnz r:31, r:7, .return addr
				shrd r:5, r:5, r:4, r:3
				add r:0, r:0, 1
				sub r:6, r:6, 1
				cmpe r:7, r:0, r:2
					cmovnz r:31, r:7, .return addr
			cmpe r:7, r:6, 0
			cmovz r:31, r:7, .read_dword addr
		lds [r:1], r:5
		mov r:5, 0
		add r:1, r:1, 1
		mov r:31, .read_loop addr

		.return:
			mov r:3, 3
			shl r:6, r:6, r:3
			shr r:5, r:5, r:6
			lds [r:1], r:5
			lds r:31, [r:30]
end if