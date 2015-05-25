//#include <stdio.h>
//#include <string.h>

#define some_constant 99
//#define typename(x) _Generic((x),  int: "int",   default: "other")

int is_integer(char * name) {
    return !strcmp(name, "int");
}

int main(int argc, char **argv) {
    // Implementation
    int high_score[20];
    // Implementation

    high_score[0]=50;
    high_score[1] = some_constant;

    if (sizeof(high_score) == 80 && is_integer(typename(high_score[0]))){
        printf("secret code\n");
    } else {
        printf("fail\n");
    }
    return 0;
}
