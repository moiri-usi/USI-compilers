	.file	"f.c"
	.text
	.globl	f_while
	.type	f_while, @function
f_while:
.LFB12:
	.cfi_startproc
.L2:
	jmp	.L2
	.cfi_endproc
.LFE12:
	.size	f_while, .-f_while
	.globl	main
	.type	main, @function
main:
.LFB13:
	.cfi_startproc
	call	f_while
	.cfi_endproc
.LFE13:
	.size	main, .-main
	.ident	"GCC: (Ubuntu/Linaro 4.6.3-1ubuntu5) 4.6.3"
	.section	.note.GNU-stack,"",@progbits
