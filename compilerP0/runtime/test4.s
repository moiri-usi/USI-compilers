	.file	"test4.c"
	.comm	C,4,4
	.comm	D,4,4
	.section	.rodata
.LC0:
	.string	"f"
.LC1:
	.string	"m"
.LC2:
	.string	"n"
	.text
	.globl	main
	.type	main, @function
main:
.LFB3:
	.cfi_startproc
	pushl	%ebp
	.cfi_def_cfa_offset 8
	.cfi_offset 5, -8
	movl	%esp, %ebp
	.cfi_def_cfa_register 5
	pushl	%ebx
	andl	$-16, %esp
	subl	$112, %esp
	.cfi_offset 3, -12
	call	setup_classes
	movl	C, %eax
	movl	%eax, (%esp)
	call	create_object
	movl	%eax, 28(%esp)
	movl	D, %eax
	movl	%eax, (%esp)
	call	create_object
	movl	%eax, 32(%esp)
	movl	$1, (%esp)
	call	inject_int
	movl	%eax, 36(%esp)
	movl	$3, (%esp)
	call	inject_int
	movl	%eax, 40(%esp)
	movl	36(%esp), %eax
	movl	%eax, 8(%esp)
	movl	$.LC0, 4(%esp)
	movl	28(%esp), %eax
	movl	%eax, (%esp)
	call	set_attr
	movl	36(%esp), %eax
	movl	%eax, 8(%esp)
	movl	$.LC0, 4(%esp)
	movl	32(%esp), %eax
	movl	%eax, (%esp)
	call	set_attr
	movl	$.LC1, 4(%esp)
	movl	28(%esp), %eax
	movl	%eax, (%esp)
	call	get_attr
	movl	%eax, 44(%esp)
	movl	44(%esp), %eax
	movl	%eax, (%esp)
	call	get_function
	movl	%eax, 48(%esp)
	movl	48(%esp), %eax
	movl	%eax, (%esp)
	call	get_fun_ptr
	movl	%eax, 52(%esp)
	movl	52(%esp), %eax
	movl	%eax, 56(%esp)
	movl	44(%esp), %eax
	movl	%eax, (%esp)
	call	get_receiver
	movl	%eax, (%esp)
	movl	56(%esp), %eax
	call	*%eax
	movl	%eax, 60(%esp)
	movl	$.LC1, 4(%esp)
	movl	32(%esp), %eax
	movl	%eax, (%esp)
	call	get_attr
	movl	%eax, 64(%esp)
	movl	64(%esp), %eax
	movl	%eax, (%esp)
	call	get_function
	movl	%eax, 68(%esp)
	movl	68(%esp), %eax
	movl	%eax, (%esp)
	call	get_fun_ptr
	movl	%eax, 72(%esp)
	movl	72(%esp), %eax
	movl	%eax, 76(%esp)
	movl	64(%esp), %eax
	movl	%eax, (%esp)
	call	get_receiver
	movl	%eax, (%esp)
	movl	76(%esp), %eax
	call	*%eax
	movl	%eax, 80(%esp)
	movl	$.LC2, 4(%esp)
	movl	32(%esp), %eax
	movl	%eax, (%esp)
	call	get_fun_ptr_from_attr
	movl	%eax, 84(%esp)
	movl	40(%esp), %eax
	movl	%eax, 4(%esp)
	movl	32(%esp), %eax
	movl	%eax, (%esp)
	movl	84(%esp), %eax
	call	*%eax
	movl	$.LC1, 4(%esp)
	movl	32(%esp), %eax
	movl	%eax, (%esp)
	call	get_attr
	movl	%eax, 88(%esp)
	movl	88(%esp), %eax
	movl	%eax, (%esp)
	call	get_function
	movl	%eax, 92(%esp)
	movl	92(%esp), %eax
	movl	%eax, (%esp)
	call	get_fun_ptr
	movl	%eax, 96(%esp)
	movl	96(%esp), %eax
	movl	%eax, 100(%esp)
	movl	88(%esp), %eax
	movl	%eax, (%esp)
	call	get_receiver
	movl	%eax, (%esp)
	movl	100(%esp), %eax
	call	*%eax
	movl	%eax, 104(%esp)
	movl	60(%esp), %eax
	movl	%eax, (%esp)
	call	project_int
	movl	%eax, %ebx
	movl	80(%esp), %eax
	movl	%eax, (%esp)
	call	project_int
	addl	%eax, %ebx
	movl	104(%esp), %eax
	movl	%eax, (%esp)
	call	project_int
	addl	%ebx, %eax
	movl	%eax, (%esp)
	call	inject_int
	movl	%eax, 108(%esp)
	movl	60(%esp), %eax
	movl	%eax, (%esp)
	call	print_any
	movl	80(%esp), %eax
	movl	%eax, (%esp)
	call	print_any
	movl	104(%esp), %eax
	movl	%eax, (%esp)
	call	print_any
	movl	108(%esp), %eax
	movl	%eax, (%esp)
	call	print_any
	movl	$0, %eax
	movl	-4(%ebp), %ebx
	leave
	.cfi_restore 5
	.cfi_def_cfa 4, 4
	.cfi_restore 3
	ret
	.cfi_endproc
.LFE3:
	.size	main, .-main
	.type	setup_classes, @function
setup_classes:
.LFB4:
	.cfi_startproc
	pushl	%ebp
	.cfi_def_cfa_offset 8
	.cfi_offset 5, -8
	movl	%esp, %ebp
	.cfi_def_cfa_register 5
	subl	$56, %esp
	movl	$0, (%esp)
	call	inject_int
	movl	%eax, -32(%ebp)
	movl	$1, (%esp)
	call	inject_int
	movl	%eax, -28(%ebp)
	movl	-32(%ebp), %eax
	movl	%eax, (%esp)
	call	create_list
	movl	%eax, -24(%ebp)
	movl	-28(%ebp), %eax
	movl	%eax, (%esp)
	call	create_list
	movl	%eax, -20(%ebp)
	movl	-24(%ebp), %eax
	movl	%eax, (%esp)
	call	create_class
	movl	%eax, C
	movl	-24(%ebp), %eax
	movl	%eax, 4(%esp)
	movl	$C_m, (%esp)
	call	create_closure
	movl	C, %edx
	movl	%eax, 8(%esp)
	movl	$.LC1, 4(%esp)
	movl	%edx, (%esp)
	call	set_attr
	movl	C, %eax
	movl	%eax, 8(%esp)
	movl	-32(%ebp), %eax
	movl	%eax, 4(%esp)
	movl	-20(%ebp), %eax
	movl	%eax, (%esp)
	call	set_subscript
	movl	-20(%ebp), %eax
	movl	%eax, (%esp)
	call	create_class
	movl	%eax, D
	movl	-24(%ebp), %eax
	movl	%eax, 4(%esp)
	movl	$D_m, (%esp)
	call	create_closure
	movl	%eax, -16(%ebp)
	movl	-24(%ebp), %eax
	movl	%eax, 4(%esp)
	movl	$D_m, (%esp)
	call	create_closure
	movl	D, %edx
	movl	%eax, 8(%esp)
	movl	$.LC1, 4(%esp)
	movl	%edx, (%esp)
	call	set_attr
	movl	-24(%ebp), %eax
	movl	%eax, 4(%esp)
	movl	$D_n, (%esp)
	call	create_closure
	movl	%eax, -12(%ebp)
	movl	-24(%ebp), %eax
	movl	%eax, 4(%esp)
	movl	$D_n, (%esp)
	call	create_closure
	movl	D, %edx
	movl	%eax, 8(%esp)
	movl	$.LC2, 4(%esp)
	movl	%edx, (%esp)
	call	set_attr
	leave
	.cfi_restore 5
	.cfi_def_cfa 4, 4
	ret
	.cfi_endproc
.LFE4:
	.size	setup_classes, .-setup_classes
	.globl	C_m
	.type	C_m, @function
C_m:
.LFB5:
	.cfi_startproc
	pushl	%ebp
	.cfi_def_cfa_offset 8
	.cfi_offset 5, -8
	movl	%esp, %ebp
	.cfi_def_cfa_register 5
	subl	$24, %esp
	movl	$.LC0, 4(%esp)
	movl	8(%ebp), %eax
	movl	%eax, (%esp)
	call	get_attr
	leave
	.cfi_restore 5
	.cfi_def_cfa 4, 4
	ret
	.cfi_endproc
.LFE5:
	.size	C_m, .-C_m
	.globl	D_m
	.type	D_m, @function
D_m:
.LFB6:
	.cfi_startproc
	pushl	%ebp
	.cfi_def_cfa_offset 8
	.cfi_offset 5, -8
	movl	%esp, %ebp
	.cfi_def_cfa_register 5
	subl	$40, %esp
	movl	$.LC0, 4(%esp)
	movl	8(%ebp), %eax
	movl	%eax, (%esp)
	call	get_attr
	movl	%eax, -16(%ebp)
	movl	-16(%ebp), %eax
	movl	%eax, (%esp)
	call	project_int
	movl	%eax, -12(%ebp)
	movl	-12(%ebp), %eax
	addl	$1, %eax
	movl	%eax, (%esp)
	call	inject_int
	leave
	.cfi_restore 5
	.cfi_def_cfa 4, 4
	ret
	.cfi_endproc
.LFE6:
	.size	D_m, .-D_m
	.globl	D_n
	.type	D_n, @function
D_n:
.LFB7:
	.cfi_startproc
	pushl	%ebp
	.cfi_def_cfa_offset 8
	.cfi_offset 5, -8
	movl	%esp, %ebp
	.cfi_def_cfa_register 5
	subl	$24, %esp
	movl	12(%ebp), %eax
	movl	%eax, 8(%esp)
	movl	$.LC0, 4(%esp)
	movl	8(%ebp), %eax
	movl	%eax, (%esp)
	call	set_attr
	movl	$0, (%esp)
	call	inject_big
	leave
	.cfi_restore 5
	.cfi_def_cfa 4, 4
	ret
	.cfi_endproc
.LFE7:
	.size	D_n, .-D_n
	.ident	"GCC: (Ubuntu/Linaro 4.6.3-1ubuntu5) 4.6.3"
	.section	.note.GNU-stack,"",@progbits
