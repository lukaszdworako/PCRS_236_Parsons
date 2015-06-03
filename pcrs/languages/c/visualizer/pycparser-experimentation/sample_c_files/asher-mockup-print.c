#include <stdio.h>

int main() {
	int num = 16; 
	printf("name:num line:4 val:%d address:%p\n", num, &num);
	char c1 = 'a';
	printf("name:c1 line:5 val:%c address:%p\n", c1, &c1);
	char c2; 
	printf("name:c2 line:6 val:%c address:%p\n", c2, &c2);
	c2 = 'b'; 
	printf("name:c2 line:7 val:%c address:%p\n", c2, &c2);
	long big_num = 3000000000; 
	printf("name:big_num line:8 val:%lu address:%p size:%d\n", big_num, &big_num, sizeof(big_num));
	int *ptr = &num;
	printf("name:ptr line:9 val:%p address:%p size:%d\n", ptr, &ptr, sizeof(ptr));
	*ptr = 32;
	printf("name:ptr line:10 val:%d address:%p\n", *ptr, &(*ptr));
	return 0;
}	