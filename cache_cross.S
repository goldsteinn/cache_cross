// abf-off
#define LOOP_CNT (1000 * 1000 * 1000)
// abf-on

    /* Just #define for NOP{N}. */
#include "nops.h"
#define XOR	0
#define MOV	1
#define DSB0	2
#define DSB1	3
#define DSB2	4
#define DSB3	5

#ifdef RUNALL
# include "padding.h"
#else
# define PAYLOAD	DSB0

	/* Just to see if certain cacheline offsets within a page may
	   change things. So far nothing.  */
# define CACHE_PADDING	NOP0

	/* Offset within cache line. Using NOP12, NOP28, NOP44, and
	   NOP60.  */
# define LOOP_PADDING	NOP60
#endif
	.global	_start
	.text
_start:
	movl	$LOOP_CNT, %ecx
	leaq	(2048 + buf_start)(%rip), %rsp
	movq	%rsp, %rsi
	leaq	64(%rsi), %rdi

	/* Page align.  */
	.p2align 12

	/* Padding config.  */
	LOOP_PADDING

	/* Loop is 8 bytes.  */
loop:
#if PAYLOAD == XOR
	/* Payload where loop is really just the decl/jnz.  */
	xorl	%eax, %eax
	xorl	%edx, %edx
#elif PAYLOAD == MOV
	/* Payload testing if it has to do with memory bandwidth.  */
	movl	(%rsi), %eax
	movl	(%rdi), %edx
#elif PAYLOAD == DSB0
	/* Payload testing how being able to run out of the LSD vs DSB
	   changes things. LSD disabling behavior in first fetch block.  */
	popq	%rax
	movq	%rsi, %rsp
#elif PAYLOAD == DSB1
	/* Payload testing how being able to run out of the LSD vs DSB
	   changes things. LSD disabling behavior in second fetch block.
	 */
	movq	%rsi, %rsp
	popq	%rax
#elif PAYLOAD == DSB2
	/* Payload testing how being able to run out of the LSD vs DSB
	   changes things. LSD disabling behavior in first fetch block and
	   non-eliminatable mov cache line.  */
	popq	%rax
	leaq	(%rsi), %rsp
#elif PAYLOAD == DSB3
	/* Payload testing how being able to run out of the LSD vs DSB
	   changes things. LSD disabling behavior in second fetch block and
	   non-eliminatable first cache line.  */
	leaq	(%rsi), %rsp
	popq	%rax
#else
# error NO PAYLOAD
#endif
	decl	%ecx
	jnz	loop

	movl	$60, %eax
	xorl	%edi, %edi
	syscall

	.section .data
	.balign	4096
buf_start:	.space 4096
buf_end:
