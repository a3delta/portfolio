// Author: a3delta
// About: This program is used to generate the first 8 numbers in a fibonacci sequence following 0 and 1.

#include <stdio.h>

//main
int main(){

    int fibarr[10] = {0,1};         //10 element arr for fib nums, initialized

    //loop to find the next 8 numbers in the sequence
    for(int i=2; i<10; i++){
        //current fib element = 2 elements back + 1 element back
        fibarr[i] = fibarr[i-2] + fibarr[i-1];
    }

    //loop to print all 10 numbers in the sequence
    for(int i=0; i<10; i++){
        //print current element in array
        printf("%d\n", fibarr[i]);
    }

    return 0;

}
