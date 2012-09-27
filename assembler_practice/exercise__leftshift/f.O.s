	.file	"f.c"
	.text
	.globl	f_leftshift
	.type	f_leftshift, @function
f_leftshift:
.LFB12:
	.cfi_startproc
	movl	$64, %eax
	ret
	.cfi_endproc
.LFE12:
	.size	f_leftshift, .-f_leftshift
	.globl	main
	.type	main, @function
main:
.LFB13:
	.cfi_startproc
	pushl	%ebp
	.cfi_def_cfa_offset 8
	.cfi_offset 5, -8
	movl	%esp, %ebp
	.cfi_def_cfa_register 5
	andl	$-16, %esp
	subl	$16, %esp
	movl	$0, (%esp)
	call	exit
	.cfi_endproc
.LFE13:
	.size	main, .-main
	.ident	"GCC: (Ubuntu/Linaro 4.6.3-1ubuntu5) 4.6.3"
	.section	.note.GNU-stack,"",@progbits
