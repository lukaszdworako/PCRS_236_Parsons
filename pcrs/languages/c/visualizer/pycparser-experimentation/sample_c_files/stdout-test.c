#include <stdio.h>

int main() {
	printf("Starting my program, hello world!\n");
	int i = 10;
	printf("The value inside of i is %d", i);
	printf("Oops I forgot a new line above!!!\n");
	char x[1];
	x[0] = 'a';
	fprintf(stderr, "error!!!");
	printf("my char array has %c in it\n", x[0]);
	printf("bye!\n");
	fprintf(stderr, "some more errors\n");
	return 0;
}