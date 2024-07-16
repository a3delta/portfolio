// Author: a3delta
// About: This program is used to generate the first 8 numbers in a fibonacci sequence following 0 and 1.

	.data					// data section

	.text					// program section
	.global main			// main
	.arch armv8-a+fp+simd	// processor type
	.type main, %function	// main function

main:
        SUBI SP,SP,#80          ; //setup stack -> sub 80 for fibarr
        STUR XZR,[SP,#0]        ; //initialize first element as 0
        STUR #1,[SP,#8]         ; //initialize second element as 1
        LDUR X9,[SP,#0]         ; //load base address of fibarr[0] to X9
        ADD X10,XZR,#16         ; //setup i initalized as 2 (2*8 bits) in X10
for1:   SUBI X11,X10,#16        ; //calc i-(2*8), store in X11
        LDUR X12,[X9,X11]       ; //load element 2 before i into X12
        ADDI X11,X11,#8         ; //calc i-(1*8), store in X11
        LDUR X13,[X9,X11]       ; //load element 1 before i into X13
        ADD X11,X12,X13         ; //add loaded elements and store in X11
        STUR X11,[X9,X10]       ; //store X11 into element at i
        ADDI X10,X10,#8         ; //increment i by 1*8
        SUBI X11,X10,#80        ; //test if i = 10*8 (array size)
        CBNZ X11,for1           ; //if it doesn't, branch to top of for1
        LDUR X0,X9              ; //load base address of fibarr[] into X0
        BL printf               ; //branch and link to printf for output

        MOV X10,XZR             ; //setup int i initalized as 0
for2:   LDUR X0,[X9,X10]        ; //load output value for fibarr[i] into X0
        BL printf               ; //branch and link to printf for output
        ADDI X10,X10,#8         ; //increment i by 1*8
        SUBI X11,X10,#80        ; //test if i = 10*8 (array size)
        CBNZ X11,for2           ; //if it doesn't, branch to top of for2
        ADDI SP,SP,#80          ; //clear the stack allocation
Exit:
