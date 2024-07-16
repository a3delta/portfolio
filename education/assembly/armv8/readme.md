
Author: a3delta

---------------------------------
Program 1 - Fibonacci Sequence
---------------------------------
Assumptions:
1. SP, the Stack Pointer, needs to have 80 bits subtracted to 
   make room for 10 8-bit elements for fibarr[].
2. Register X9 is used to hold the base address of fibarr[].
3. Register X10 is used as i for FOR loop functionality.
4. Register X11 is used to hold offsets from i to work with 
   elements prior to fibarr[i].
5. Register X12 is used to hold fibarr[i-2] from the stack.
6. Register X13 is used to hold fibarr[i-1] from the stack.
7. Register X11 is re-used to hold the sum of fibarr[i-2] and 
   fibarr[i-1], overwriting the i offset.
8. The sum held in X11 is stored back on the stack at fibarr[i].
9. Register X11 is re-used to hold the result of comparisons  
   for use with conditional branches.
10.SP has 80 bits added back to it once the module run is done.
11.Register X0 is used for data output.

---------------------------------
Program 2 - Vector Product
---------------------------------
Assumptions:
1. SP, the Stack Pointer, needs to have 80 bits subtracted to 
   make room for 2 arrays of 5 8-bit elements, a[] and b[].
2. Register X9 is used to hold the base address of a[].
3. Register X10 is used to hold the base address of b[].
4. Register X11 is used as i for initialization values.
5. Register X12 is used as j for FOR loop functionality.
6. Register X13 is used to hold the result of comparisons 
   for use with conditional branches.
7. Register X11 is re-initialized to 0 for use as the sum.
8. Register X14 is used to hold a[j] for multiplication.
9. Register X15 is used to hold b[j] for multiplication.
10.Register X16 is used to hold prod = a[j] * b[j].
11.SP has 80 bits added back to it once the module run is done.
12.Register X0 is used for data output.

---------------------------------
Program 3 - String Manipulation
---------------------------------
Assumptions:
1. Line is a pre-defined sentence in the .data section.
2. The base address of Line[] is assumed to be in R0.
3. Register X10 is used to hold the word count.
4. Register X11 is used as i for FOR loop functionality.
5. Register X12 is used to hold the base address of Line[].
6. Register X13 is used to hold the result of comparison 
   operations for use with conditional branchs.
7. Register X14 is used as a flag to identify new words.
8. Register X15 is used to hold Line[i] for comparison and 
   manipulation.
9. Register X0 is used for data output.

-----------------------------------
Program 4 - Cosine Value
-----------------------------------
Assumptions:
1. X0  - Register used for result of cosine calc initialization.
   D0  - Used for final result as a float with double precision.
2. D1  - Register for input variable x, a double precision float.
3. X2  - Register for input variable a, an int for the upper 
         limit of the sum loop.
4. X3  - Register used for result of -1^n.
   D3  - Used for the result of -1^n converted to a double float.
5. D4  - Register used for result of x^2n.
6. X5  - Register used for result of 2n!.
   D5  - Used for 2n! converted to double float for final calc.
7. X9  - Register for tier 1 loop variable (outermost loop).
         Used in cosine summation. Do not want to overwrite.
8. X10 - Register for tier 2 loop variable (secondary loop).
         Used in power and factorial loops. Loops begin and end 
         within the functions in which they are called.
9. X11 - Register for the value of n (n or 2n).
10.X12 - Register for base value of power function (x or -1).
   D12 - Used for the base value of power func as a double float.
11.X13 - Register for result of power function. Result is moved 
         from X13 into X3 or X4 within the cosine function.
   D13 - Used for the power func result converted to a double float.

Function - Power - Assumptions
-----------------------------------
1. X10 - Register to track tier 2 (inner) loop, initialized to 0.
2. X13 - Register to initialize result of function with a^0.
3. D13 - Register to hold result of function as a double float.
4. X14 - Register to compare X10 (loop count) to X11 (loop limit).
5. D12 - Register to hold base value, a, as a double float.
         Passed into function.

Function - Factorial - Assumptions
-----------------------------------
1. X5  - Register to hold result of 2n!.
2. X11 - Register to hold value of n passed into function.
         Decremented each loop, then multiplied with X5.

Function - Cosine - Assumptions
-----------------------------------
1. X9  - Register to track tier 1 (outer) loop, initialized to 0.
2. X0  - Register to hold running sum of cosx, init to 0.
3. D0  - X0 converted from signed int to double float.
4. X2  - Register for input variable a, upper limit of sum loop.
5. X14 - Register used for branch comparisons.
6. X11 - Register used for power exponent, n.
         Init to n for first pass, re-init to 2n for second pass.
7. X12 - Register for base of power func, init to -1 for first pass.
8. D12 - X12 converted from signed int to double float.
         Re-init as x (D1) for second call of power func.
9. D6  - Register used as a double float zero register (ZR).
         This is used because I don't know the syntax for existing ZR.
10.D3  - Register to hold result of -1^n.
11.D13 - Register containing the result returned from power func.
12.D1  - Register to hold value of input x, base of x^2n.
13.D4  - Register to hold result of x^2n.
14.D5  - Register to hold conversion of X5 from signed int to double.
15.D14 - Register to hold calc of cosx function, added to sum in D0.
