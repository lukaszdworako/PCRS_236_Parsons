#include <stdio.h>

int add_two(int i, int j);

int main() {
	int l = 1;
	int m = 5;
	int k;
	k = add_two(l, m);
	printf("k is %d\n", k);
	return 0;
}

int add_two(int i, int j) {
	int q = i + j;
	return q;
}