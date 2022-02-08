#include <stdio.h>

int main(){
    char *p = NULL;

    printf("I will crash whether you like it or not.");

    *p = "This is called suicide..";
}