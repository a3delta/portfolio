// Author: a3delta
// About: This program is used to calculate the cosine value of a variable.
// Function: sum_n=0->a [ ( ((-1)^n) * (x^(2n)) ) / (2n)! ]

#include <stdio.h>

//main
int main(){

    float x;                //float for x, can print this as single precision with %.1f
    int a = 0;              //int for a, might be 32 bit, int32_t requires an h include
    float top;              //for the dividend of the equation
    int n2;                 //for 2*n
    float sum = 1;          //for sum calc, init to 1 for when n=0

    //prompt for x and take input with single precision
    printf("Enter a single precision float value for x: \n");
    scanf("%f", &x);
    //prompt for a and take input until non-zero positive int is entered
    while(a < 1){
        printf("Enter a non-zero integer value for a: \n");
        scanf("%d", &a);
    }

    //sum loop
    a++;                            //increase a by 1 for sum loop
    for(int n=1; n<a; n++){         //run sum from n=1 to a, n=0 sets outcome to 0

        //initialize n2
        n2 = 2*n;

        //loop for second exponent
        top = x;                    //init to x for x^1
        for(int i=1; i<n2; i++){    //n2 = 2*n, start at 1 -> top starts at x^1
            top *= x;               //multiply top by x^2n
        }

        //if n is odd (n%2 == 1), multiply top by -1 for (-1)^n
        if(n%2 == 1){
            top *= -1;
        }

        //loop for factorial calculation
        for(int i = n2-1; i>0; i--){    //n2 = 2*n = base num for factorial
            n2 *= i;                    //mult 2n (base of the factorial) by 2n--
        }

        //calc cos(x) at n and add to the sum
        sum += ( top / n2 );

    }
    a--;                            //reduce a by 1 now that sum loop is complete

    //print out the cosine value calculated
    printf("cos(x) from 0 to %d = %.1f\n", a, sum);

    return 0;

}
