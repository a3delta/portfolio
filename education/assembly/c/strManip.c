// Author: a3delta
// About: This program is used to count words in a string and
//        make the first letter of each word upper case.

#include <stdio.h>

//main
int main(){

    char line[256];         //char array to store string, max length of 256
    int count = 0;          //int var to store count, initialized to 0

    //prompt for input
    printf("Enter a sentence up to 256 characters long: ");
    //take input up to 256 char, then clear the stdin buffer
    scanf("%255[^\n]", line);
    while((getchar()) != '\n');

    //loop through the string
    for(int i=0; i<256; i++){
    
        //find the first word and capitalize the first letter
        if(i == 0 && line[i] != ' '){
            //make char upper if in the range of lower alphabet in ASCII value
            if(line[i] > '`' && line[i] < '{'){
                //subtract 32 from ASCII value to change lower to upper
                line[i] = line[i] - 32;
            }
            //increase word count
            count++;
        }
        //find the next word and capitalize the first letter
        else if(line[i-1] == ' ' && line[i] != ' '){
            //make char upper if in the range of lower alphabet in ASCII value
            if(line[i] > '`' && line[i] < '{'){
                //subtract 32 from ASCII value to change lower to upper
                line[i] = line[i] - 32;
            }
            //increase word count
            count++;
        }
    
    }

    //print the updated line
    printf("Updated string:\n%s\n", line);
    //print count
    printf("Word count:\n%d\n", count);

    return 0;

}
