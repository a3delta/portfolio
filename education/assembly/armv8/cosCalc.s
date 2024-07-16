// Author: a3delta
// About: This program is used to calculate an approximation of cos(x).

	.data					// data section

    //double for x value in calcs
x:
    .double 3.14, 5.1, 3.0

    //int for a (upper limit of summation) value in calcs
a:
    .word 11, 27, 4

	.text					// program section
	.global main			// main
	.arch armv8-a+fp+simd	// processor type
	.type main, %function	// main function

main:
    //initialize data
        ADR X9,x     		; //init X9 with mem address of x[]
        LDUR D1,[X9,#0]		; //init D1 with float val at x[0]
        ADR X9,a     		; //init X9 with mem address of a[]
        LDUR X2,[X9,#0]		; //init with int val at a[0]
    //pass data to cosine func
Cos:    MOV X9,XZR       	; //init i (loop var) to 0
        MOV X0,XZR     		; //init X0 (final result/sum) to 0
        SCVTF D0,X0         ; //convert from X0 (int) to D0 (dp float)
        SUB X14,X2,X9       ; //X14 = a - i
        CBZ X14,CosEx       ; //if X14 == 0, exit cosine func
CosLp:  ADD X9,X9,#1        ; //i++
        ADD X11,X9,XZR      ; //set X11 (exp of power func) to n (i)
        MOV X12,XZR			; //init X12 to 0
        SUB X12,X12,#1      ; //set X12 (base of power func) to -1
        SCVTF D12,X12       ; //convert X12 (int) to D12 (dp float) (signed)
        BL Power            ; //call power func to calc -1^n
        SCVTF D6,XZR        ; //convert XZR to D6 - not sure if DZR is a thing
        FADD D3,D13,D6      ; //set D3 (result of -1^n)
        LSL X11,X9,#1       ; //set X11 (exp of power func) to 2n (2i)
        FADD D12,D1,D6      ; //set D12 (base of power func) to x
        BL Power            ; //call power func to calc x^2n
        FADD D4,D13,D6      ; //set D4 (result of x^2n)
        BL Fact             ; //call factorial func to calc 2n!
        SCVTF D5,X5         ; //convert X5 from int to dp float
        FMUL D14,D3,D4      ; //D14 = -1^n * x^2n
        FDIV D14,D14,D5     ; //D14 = D14 / 2n!
        FADD D0,D0,D14      ; //D0 (final result) = D0 + D14
        SUB X14,X2,X9       ; //X14 = a - i
        CBNZ X14,CosLp      ; //if X14 != 0, continue sum loop
        ; //save data from cosine func to data area? declare some blank var and store it?
          //saw a hello world that had a hex code by the text to make it auto print?
    //store result on stack
CosEx:  SUB SP,SP,#64       ; //subtract size of double (64b) from stack
        STUR D0,[SP,#0]     ; //store value of result to stack
    //power function
Power:  MOV X10,XZR     	; //init X10 to 0 for tier 2 loop
		MOV X13,XZR			; //init X13 to 0
        ADD X13,X13,#1      ; //init X13 (power result) to a^0 = 1
        SCVTF D13,X13       ; //convert X13 (power result) from int to dp float
        SUB X14,X11,X10     ; //X14 = n (loop limit) - j (loop var)
        CBZ X14,PwrEx       ; //if X14 == 0, then exit power func
PwrLp:  ADD X10,X10,#1      ; //j++ -> increment loop var
        FMUL D13,D13,D12    ; //D13 = D13 * a -> float w/ double prec
        SUB X14,X11,X10     ; //X14 = n (loop limit) - j (loop var)
        CBNZ X14,PwrLp      ; //if X14 != 0, continue for loop
PwrEx:  BR X30              ; //branch back to where called from
    //factorial function
Fact:   MOV X5,XZR			; //init X5 to 0
		ADD X5,X5,#1        ; //fact results init with 1, 0! = 1
        CBZ X11,FactEx      ; //if n == 0, exit Fact loop
        ADD X5,X11,XZR      ; //results re-init with n when n != 0
        SUB X11,X11,#1      ; //n-- -> decrement n for next fact value
        CBZ X11,FactEx      ; //if n == 0, exit Fact loop
FactLp: MUL X5,X5,X11       ; //X5 (fact result) = X5 * n (current val)
        SUB X11,X11,#1      ; //n-- -> decrement n for next fact value
        CBNZ X11,FactLp     ; //if n != 0, continue loop
FactEx: BR X30              ; //branch back to where called from
Exit:
