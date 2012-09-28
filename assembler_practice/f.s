	.file	"f.c"
	.text
	.globl	f_notEqual
	.type	f_notEqual, @function
f_notEqual:
.LFB0:
	.cfi_startproc
	pushl	%ebp
	.cfi_def_cfa_offset 8
	.cfi_offset 5, -8
	movl	%esp, %ebp
	.cfi_def_cfa_register 5
	subl	$16, %esp
	movl	$1, -4(%ebp)
	cmpl	$2, -4(%ebp)
	je	.L2
	movl	$2, -4(%ebp)
.L2:
	movl	-4(%ebp), %eax
	leave
	.cfi_restore 5
	.cfi_def_cfa 4, 4
	ret
	.cfi_endproc
.LFE0:
	.size	f_notEqual, .-f_notEqual
	.globl	f_smallerThan
	.type	f_smallerThan, @function
f_smallerThan:
.LFB1:
	.cfi_startproc
	pushl	%ebp
	.cfi_def_cfa_offset 8
	.cfi_offset 5, -8
	movl	%esp, %ebp
	.cfi_def_cfa_register 5
	subl	$16, %esp
	movl	$1, -4(%ebp)
	cmpl	$1, -4(%ebp)
	jg	.L4
	movl	$2, -4(%ebp)
.L4:
	movl	-4(%ebp), %eax
	leave
	.cfi_restore 5
	.cfi_def_cfa 4, 4
	ret
	.cfi_endproc
.LFE1:
	.size	f_smallerThan, .-f_smallerThan
	.globl	f_arr
	.type	f_arr, @function
f_arr:
.LFB2:
	.cfi_startproc
	pushl	%ebp
	.cfi_def_cfa_offset 8
	.cfi_offset 5, -8
	movl	%esp, %ebp
	.cfi_def_cfa_register 5
	subl	$16, %esp
	movl	$1, -8(%ebp)
	movl	$2, -4(%ebp)
	movl	-4(%ebp), %eax
	leave
	.cfi_restore 5
	.cfi_def_cfa 4, 4
	ret
	.cfi_endproc
.LFE2:
	.size	f_arr, .-f_arr
	.globl	f_power
	.type	f_power, @function
f_power:
.LFB3:
	.cfi_startproc
	pushl	%ebp
	.cfi_def_cfa_offset 8
	.cfi_offset 5, -8
	movl	%esp, %ebp
	.cfi_def_cfa_register 5
	subl	$16, %esp
	movl	$3, -8(%ebp)
	movl	$2, -4(%ebp)
	movl	-4(%ebp), %eax
	movl	-8(%ebp), %edx
	xorl	%edx, %eax
	leave
	.cfi_restore 5
	.cfi_def_cfa 4, 4
	ret
	.cfi_endproc
.LFE3:
	.size	f_power, .-f_power
	.globl	f_leftshift
	.type	f_leftshift, @function
f_leftshift:
.LFB4:
	.cfi_startproc
	pushl	%ebp
	.cfi_def_cfa_offset 8
	.cfi_offset 5, -8
	movl	%esp, %ebp
	.cfi_def_cfa_register 5
	pushl	%ebx
	subl	$16, %esp
	movl	$16, -16(%ebp)
	movl	$2, -12(%ebp)
	movl	-12(%ebp), %eax
	movl	-16(%ebp), %edx
	movl	%edx, %ebx
	.cfi_offset 3, -12
	movl	%eax, %ecx
	sall	%cl, %ebx
	movl	%ebx, %eax
	movl	%eax, -8(%ebp)
	movl	-8(%ebp), %eax
	addl	$16, %esp
	popl	%ebx
	.cfi_restore 3
	popl	%ebp
	.cfi_def_cfa 4, 4
	.cfi_restore 5
	ret
	.cfi_endproc
.LFE4:
	.size	f_leftshift, .-f_leftshift
	.globl	f_while
	.type	f_while, @function
f_while:
.LFB5:
	.cfi_startproc
	pushl	%ebp
	.cfi_def_cfa_offset 8
	.cfi_offset 5, -8
	movl	%esp, %ebp
	.cfi_def_cfa_register 5
.L9:
	jmp	.L9
	.cfi_endproc
.LFE5:
	.size	f_while, .-f_while
	.globl	main
	.type	main, @function
main:
.LFB6:
	.cfi_startproc
	pushl	%ebp
	.cfi_def_cfa_offset 8
	.cfi_offset 5, -8
	movl	%esp, %ebp
	.cfi_def_cfa_register 5
	andl	$-16, %esp
	subl	$16, %esp
	call	f_notEqual
	call	f_smallerThan
	call	f_arr
	call	f_power
	call	f_leftshift
	call	f_while
	movl	$0, (%esp)
	call	exit
	.cfi_endproc
.LFE6:
	.size	main, .-main
	.ident	"GCC: (Ubuntu/Linaro 4.6.3-1ubuntu5) 4.6.3"
	.section	.note.GNU-stack,"",@progbits
