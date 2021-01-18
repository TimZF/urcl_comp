
#define shiftValue 8
#define fixedP int


int int2fixed(int x){
	return x<<shiftValue;
}

int fixed2int(int x){
	return x>>shiftValue;
}

int round(int x){
	int out = (x>>shiftValue);
	if((x<<shiftValue)<0){out++;}
	return out;
}

void fixedPrint(int x){
	int num = x>>shiftValue;
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
	

	__debugScreen__('.');
	int fracParts = x<<shiftValue>>shiftValue;
	if(fracParts == 0){
		__debugScreen__('0');
	}
	else{
		while (fracParts > 0) {
    		fracParts = fracParts*10;
    		__debugScreen__('0' + (fracParts >> shiftValue));
    		fracParts = fracParts & ((1 << shiftValue) - 1);
		}
	}
}

void fixed2Str(int fpnum, char* res){
	int num = fpnum>>shiftValue<<shiftValue;
	int dgcount = digit_count(num);

	int index = dgcount - 1;
	char x;
	if(num == 0 ){
		res[0] = '0';
	}
	
	while(num != 0){
		modulo_divide(&num, &x, num, 10);
		res[index] = x + '0';
		index--;
	}
	index = dgcount;
	int fracParts = x<<shiftValue>>shiftValue;
	while (fracParts > 0) {
    	fracParts = fracParts*10;
    	res[index] = '0' + (fracParts >> shiftValue);
    	index++;
    	fracParts = fracParts & ((1 << shiftValue) - 1);
	}
	res[index] = '\0';
}

//void setBitShift(int x){
//
//}

void fixedDiv(int* result, int x, int y){
	divide(result, x, y>>shiftValue);
}

void fixedMul(int* result, int x, int y){
	*result = x*(y>>shiftValue);
}
