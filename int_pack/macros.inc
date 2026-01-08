macro lds op1, op2{
	match r1 [r2], op1 op2\{
		inm r1, r2
	rept 0\{\} match r1 [r2], op2 op1\{
		outm r1, r2
	\}
}

macro entry point{
	local any
	virtual at point
		entry_point:
	end virtual
	any = entry_point
}

macro _push arg{
	match =r:n, arg\{
		if n = 30
			mov r:29, arg
			sub r:30, r:30, 1
			lds [r:30], r:29
		else
			sub r:30, r:30, 1
			lds [r:30], arg
		end if
	rept 0\{\}rept 1\{
		match [any], arg\\{
			lds r:29, arg
		rept 0\\{\\} rept 1\\{
			mov r:29, arg
		\\}
		sub r:30, r:30, 1
		lds [r:30], r:29
	\}
}

macro _pop arg{
	match [any], arg\{
		lds r:29, [r:30]
		lds arg, r:29
	rept 0\{\} rept 1\{
		lds arg, [r:30]
	\}
	add r:30, r:30, 1
}

macro ccall name, [args]{
	common
	local cntr, _any, any
	cntr = 1
	match _any, args\{
		forward
		match [any], args\\{
			match =r:n, any\\\{
				lds r:cntr, args
			rept 0\\\{\\\}rept 1\\\{
			display \\`any
				mov r:cntr, any addr
				lds r:cntr, [r:cntr]
			\\\}
		rept 0\\{\\} rept 1 \\{
			match =r:n, args\\\{
				if cntr <> n
					mov r:cntr, args
				end if
			rept 0\\\{\\\} rept 1 \\\{
				mov r:cntr, args 
			\\\}
		\\}
		cntr = cntr + 1
		common
	\}
	local ..ret_addr
	_push ..ret_addr addr
	match [any], name\{
		match =r:n, any\\{
			lds r:31, name
		rept 0\\{\\}rept 1\\{
			mov r:29, any
			lds r:31, [r:29]
		\\}
	rept 0\{\} rept 1\{
		mov r:31, name addr
	\}
	..ret_addr:
	add r:30, r:30, 1
}

if used entry_point
	mov r:30, 4096
	mov r:31, entry_point addr
end if