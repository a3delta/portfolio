// Author: a3delta
// About: This program is used to count words in a string and
//        make the first letter of each word upper case.

	.data					// data section

    //setup a 5+ word sentence in the .data section
Line:
    .asciz "here is a short sentence to manipulate\n\0"

	.text					// program section
	.global main			// main
	.arch armv8-a+fp+simd	// processor type
	.type main, %function	// main function

main:
        MOV X10,XZR             ; //initialize count as 0 in X10
        MOV X11,XZR             ; //initialize array offset, i, as 0
        MOV X14,XZR             ; //initialize space flag as 0 in X14
        LDUR X12,=Line          ; //load Line[] base address into X12
        LDUR X15,[X12,X11]      ; //load Line[0] into X15
for1:   SUBI X13,X15,#0x20      ; //check if Line[i] is a space (ASCII: 32, 0x20)
        CBNZ X13,cap            ; //if not, skip to cap
        MOV X14,XZR             ; //set flag for found space to 0 in X14
        B inc                   ; //branch to inc for next element
cap:    CBNZ X14,inc            ; //check space flag, if not 0, skip to inc
        ADDI X10,X10,#1         ; //increment count by 1
        ADDI X14,XZR,#1         ; //switch space flag to 1, current char is not space
        SUBIS X13,X15,#0x61     ; //test if Line[i] >= 97 (ASCII a: 97, 0x61)
        B.LT inc                ; //if less than 97, branch to inc
        SUBIS X13,X15,#0x7A     ; //test if Line[i] <= 122 (ASCII z: 122, 0x7A)
        B.GT inc                ; //if greater than 122, branch to inc
        SUBI X15,X15,#0x20      ; //subtract 32 (0x20) from ASCII value to capitalize
        STUR X15,[X12,X11]      ; //store updated value back into Line[i]
inc:    ADDI X11,X11,#8         ; //increment i by 1*8
        LDUR X15,[X12,X11]      ; //load Line[i]
        CBNZ X15,for1           ; //if Line[i] is not \0 (NULL - ASCII: 0), branch to for1
        LDUR X0,X12             ; //load base address of b[] into X0
        BL printf               ; //branch and link to printf for output
Exit:
