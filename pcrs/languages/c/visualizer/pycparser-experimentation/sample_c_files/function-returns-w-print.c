#include <stdio.h>

int add_two(int i, int j);

int main() {
	int l = 1;
	printf("var: l val: 1 addr:%p\n", &l);
	int m = 5;
	printf("var: m val: 5 addr:%p\n", &m);
	int k;
	printf("var: k val: junk addr:%p\n", &k);
	k = add_two(l, m);
	printf("k is %d\n", k);
	return 0;
}

int add_two(int i, int j) {
	printf("var: i, j val: 1, 5 addr: %p, %p \n", &i, &j);
	int q = i + j;
	printf("var: q val: 6 addr:%p\n", &q);
	return q;
}