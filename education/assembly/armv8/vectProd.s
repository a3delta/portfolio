// Author: a3delta
// About: This program is used to generate the dot product of 2 vectors.

	.data					// data section

	.text					// program section
	.global main			// main
	.arch armv8-a+fp+simd	// processor type
	.type main, %function	// main function

main:
        SUBI SP,SP,#80          ; //setup stack -> sub 80 for a and b
        LDUR X9,[SP,#0]         ; //load base address of a[0] to X9
        LDUR X10,[SP,#40]       ; //load base address of b[0] to X10
        MOV X11,XZR             ; //setup i initalized as 0 in X11
        MOV X12,XZR             ; //setup array offset, j, as 0 in X12
init:   ADDI X11,X11,#1         ; //increment i by 1, making it odd
        STUR X11,[X9,X12]       ; //initialize a[j] as i (odd)
        ADDI X11,X11,#1         ; //increment i by 1, making it even
        STUR X11,[X10,X12]      ; //initialize b[j] as i (even)
        ADDI X12,X12,#8         ; //increment j by 1*8, for next element
        SUBI X13,X12,#40        ; //test if j = 5*8 (size of arrays)
        CBNZ X13,init           ; //if it doesn't, branch to top of init
        MOV X11,XZR             ; //re-initialize X11 to 0 to hold the sum
        MOV X12,XZR             ; //re-initialize j to 0 in X12
for1:   LDUR X14,[X9,X12]       ; //load a[j] into X14
        LDUR X15,[X10,X12]      ; //load b[j] into X15
        MUL X16,X14,X15         ; //a[j] (X14) * b[j] (X15) = prod (X16)
        ADD X11,X11,X16         ; //sum (X11) = sum (X11) + prod (X16)
        ADDI X12,X12,#8         ; //increment j by 1*8, for next element
        SUBI X16,X12,#40        ; //test if j = 5*8 (size of arrays)
        CBNZ X16,for1           ; //if it doesn't, branch to top of for1
        LDUR X0,X9              ; //load base address of a[] into X0
        BL printf               ; //branch and link to printf for output
        LDUR X0,X10             ; //load base address of b[] into X0
        BL printf               ; //branch and link to printf for output

        MOV X12,XZR             ; //setup int j initalized as 0
for2:   LDUR X0,[X9,X12]        ; //load base address of a[j] into X0
        BL printf               ; //branch and link to printf for output
        LDUR X0,[X10,X12]       ; //load base address of b[j] into X0
        BL printf               ; //branch and link to printf for output
        ADDI X12,X12,#8         ; //increment j by 1*8
        SUBI X16,X12,#40        ; //test if j = 5*8 (array size)
        CBNZ X16,for2           ; //if it doesn't, branch to top of for2
        ADDI SP,SP,#80          ; //add 80 bits back to stack to clear it
Exit:
