#include <stdio.h>
int newfunction();
int myglobal = 10;
int main(int argc, char **argv)
{
	int i;
	i = 3;
	int *array;
	int j;
	char *myptr;
	myptr = malloc(2);
	myptr = 'j';
	j = 2;
	array = j;
	if(j == 2)
	{
		j = 5;
	}
	while(j < 10)
	{
		j++;
		i++;
	}
	int funarray[3] = {2, 4, 10};
	printf("hello world%d", 2);
	printf("hey");
	int q;
	q = 4;
	return 0;
}

int newfunction(){
	return 0;
}