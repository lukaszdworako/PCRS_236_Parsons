#include <stdio.h>
#include <stdlib.h>

int can_take_wizardry(double cgpa, int credits_complete);

int main(int argc, char **argv) {

    double cgpa = atof(argv[1]);
    int credits = atoi(argv[2]);
    printf("%d",can_take_wizardry(cgpa, credits));
    return 0;
}

int can_take_wizardry(double cgpa, int credits_complete) {
    return 0;    // replace this statement with your code
}
