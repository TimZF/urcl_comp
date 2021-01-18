

#define maxCharsOnScreen 10
int scancode = 0;


int input(char *c) {
	int nChars = 0;
	while (1){
		scancode = __input__();
		if(scancode==0){
			continue;
		}
		if(scancode==10){
			break;
		}
		if(scancode>31){
			c[nChars] = scancode;
			nChars++;
		}
		if(scancode==8){
			c[nChars] = 0;
			nChars--;
		}

		printchar(scancode);
	}
	c[nChars] = 0;
	return nChars;
}


void clear_screen(){
	__asm__("OUT 3, 10");
	__asm__("OUT 3, 10");
	__asm__("OUT 3, 10");
	__asm__("OUT 3, 10");
	__asm__("OUT 3, 10");
	__asm__("OUT 3, 10");
}


void printchar(char c) {
	__debugScreen__(c);
}

void printString(char *c) {
	int x = 0;
	while (c[x]!=0){
		__debugInt__(c[x]);
		__debugScreen__(c[x]);
		x++;
	}
}

void printInt(int num) {
	int dgcount = digit_count(num);
	char* out = malloc(dgcount);

	int offset = 0;
	if(num == 0 ){
		__debugScreen__('0');
	}
	else{
		while(num != 0){
			modulo_divide(&num, out+offset, num, 10);
			offset++;
		}
		offset--;
		while(offset>=0){
			__debugScreen__('0' + out[offset]);
			offset--;
		}
	}
	free(out);
}

