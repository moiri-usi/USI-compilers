	.file	"f.c"
	.text
	.globl	f_notEqual
	.type	f_notEqual, @function
f_notEqual:
.LFB12:
	.cfi_startproc
	movl	$2, %eax
	ret
	.cfi_endproc
.LFE12:
	.size	f_notEqual, .-f_notEqual
	.globl	f_smallerThan
	.type	f_smallerThan, @function
f_smallerThan:
.LFB13:
	.cfi_startproc
	movl	$2, %eax
	ret
	.cfi_endproc
.LFE13:
	.size	f_smallerThan, .-f_smallerThan
	.globl	f_arr
	.type	f_arr, @function
f_arr:
.LFB14:
	.cfi_startproc
	movl	$2, %eax
	ret
	.cfi_endproc
.LFE14:
	.size	f_arr, .-f_arr
	.globl	f_power
	.type	f_power, @function
f_power:
.LFB15:
	.cfi_startproc
	movl	$1, %eax
	ret
	.cfi_endproc
.LFE15:
	.size	f_power, .-f_power
	.globl	f_leftshift
	.type	f_leftshift, @function
f_leftshift:
.LFB16:
	.cfi_startproc
	movl	$64, %eax
	ret
	.cfi_endproc
.LFE16:
	.size	f_leftshift, .-f_leftshift
	.globl	f_while
	.type	f_while, @function
f_while:
.LFB17:
	.cfi_startproc
.L7:
	jmp	.L7
	.cfi_endproc
.LFE17:
	.size	f_while, .-f_while
	.globl	main
	.type	main, @function
main:
.LFB18:
	.cfi_startproc
	call	f_while
	.cfi_endproc
.LFE18:
	.size	main, .-main
	.ident	"GCC: (Ubuntu/Linaro 4.6.3-1ubuntu5) 4.6.3"
	.section	.note.GNU-stack,"",@progbits
