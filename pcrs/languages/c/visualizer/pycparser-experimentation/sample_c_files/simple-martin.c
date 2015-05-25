#include <stdio.h>
#include <stdlib.h>


typedef struct ll_node {
    struct ll_node *next;
    struct ll_node *prev;
    int val;
} Node;

/*
A silly c program I made to test out the parser
*/
int main(int argc, char **argv)
{
    int i = 5;
    i = 3;
    int j;
    j = 2;

    char *myptr;
    myptr = malloc(2);
    *myptr = 'j';

    int *array;
    *array = j;

    printf("hello world%d\n", 2);
    printf("hey\n");

    int q;
    q = 4;

    int high_score[20] = {1, 2, 3};
    high_score[10] = 10;

    Node *n = malloc(sizeof(Node));

    return;
}
