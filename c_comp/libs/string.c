int digit_count(int num)
{
	int count = 0;
	if(num == 0){
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
		if (dgcount == 1){
			number[0] = '0';
			number[1] = 0;
			return;
		}
	}

	while(num != 0){
		//x = num % 10;

		modulo_divide(&num, &x, num, 10);
		//modulo(&x, num, 10);
		number[index] = x + '0';
		index--;
		//num = num / 10;
		//divide(&num, num, 10);
	}
	number[dgcount] = 0;
}


int atoi(char *number)
{
	int x = 0;
	int out = 0;
	while(number[x]!=NULL){
		out = out*10;
		out = out+(number[x]-'0');
		x++;
	}
	return out;
}





int stringLen(char *c) {
	int x = 0;
	while (c[x]!=0){
		x++;
	}
	return x;
}



int strCmp(char *c, char *c2) {
	int x = 0;
	while (true){
		if(c[x]!=c2[x]){return false;}
		if(c[x]==0){break;}
		x++;
	}
	return true;
}

