#define __STRING
#ifndef __MATH
#include "math.c"
#endif

int digit_count(int num)
{
	num = (num<<1)>>1;
	int count = 0;
	if(num<10){
		return 1;
	}

	while(num > 0){
		count++;
		divide(&num, num, 10);
	}
	return count;
}



void itoa(int num, char *number)
{
	
	int dgcount = digit_count(num);
	int index = dgcount - 1;

	char x;
	if(num == 0 ){
		number[0] = '0';
		number[1] = 0;
		return;
	}
	
	while(num != 0){
		//x = num % 10;
		//num = num / 10;

		modulo_divide(&num, &x, num, 10);
		number[index] = x + '0';
		index--;
		

	}
	number[dgcount] = 0;
}


int atoi(char *number)
{
	int x = 0;
	int out = 0;
	while(number[x]!=0){
		out = out*10;
		out = out+(number[x]-'0');
		x++;
	}
	return out;
}





int strlen(char *c) {
	int x = 0;
	while (c[x]!=0){
		x++;
	}
	return x;
}



int strcmp(char *c, char *c2) {
	int x = 0;
	while (1){
		if(c[x]!=c2[x]){return 0;}
		if(c[x]==0){break;}
		x++;
	}
	return 1;
}


void strcpy(char *c, char *c2) {
	int x = 0;
	while (1){
		if(c[x]==0){return;}
		else{c2[x] = c[x];}
		x++;
	}
}


char* strcat(char *c, char *c2) {
	char* out = calloc(strlen(c)+strlen(c2)+1, 0);
	int x = 0;
	while (c[x]!=0){
		out[x] = c[x];
		x++;
	}
	x = 0;
	while (c2[x]!=0){
		out[x] = c2[x];
		x++;
	}
	return out;
}


char* strdup(char *c) {
	char* out = calloc(strlen(c)+1, 0);
	int x = 0;
	while (c[x]!=0){
		out[x] = c[x];
		x++;
	}
	return out;
}

