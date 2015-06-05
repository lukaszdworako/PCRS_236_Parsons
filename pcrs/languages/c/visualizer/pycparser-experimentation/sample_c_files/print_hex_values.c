#include <stdio.h>

int main()
{
    unsigned long pad_length = 0;

    char c = 'a';
    int i = 4;
    long long l = 10000;
    char *ptr = malloc(sizeof(char));
    ptr = "abcd";

    pad_length = sizeof(c) * 2;
    printf("%0*X\n", pad_length, c);

    pad_length = sizeof(i) * 2;
    printf("%0*X\n", pad_length, i);

    pad_length = sizeof(l) * 2;
    printf("%0*X\n", pad_length, l);

    pad_length = sizeof(&ptr) * 2;
    printf("%0*X\n", pad_length, &ptr);

    pad_length = sizeof(ptr) * 2;
    printf("%0*X\n", pad_length, ptr);
    
    int k;
    for(k=0; k < strlen(ptr); k++) {
    	printf("%0*X", 2, *(ptr+k));
    }
    printf("\n");
    for(k=0; k < strlen(ptr); k++) {
    	printf("%c ", *(ptr+k));
    }
    printf("\n");

    return 0;
}

