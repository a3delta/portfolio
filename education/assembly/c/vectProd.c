// Author: a3delta
// About: This program is used to generate the dot product of 2 vectors.

#include <stdio.h>

//main
int main(){

    int a[5] = {1,3,5,7,9};     //5 element arr for first 5 odd nums
    int b[5] = {2,4,6,8,10};    //5 element arr for first 5 even nums
    int ans = 0;                //int to hold a sum for the final answer

    //loop to calc the product of arrays a and b at element i
    for(int i=0; i<5; i++){
        //current ans + the next product being added to the sum
        ans += a[i]*b[i];
    }

    //print vectors a and b
    printf("Vector a: ");
    for(int i=0; i<5; i++){
        printf("%d ", a[i]);
    }
    printf("\n");
    printf("Vector b: ");
    for(int i=0; i<5; i++){
        printf("%d ", b[i]);
    }
    printf("\n");

    //print the answer
    printf("a * b = %d\n", ans);

    return 0;

}
