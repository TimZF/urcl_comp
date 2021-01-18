

int arrCmp(int *c, int *c2, int len) {
	int x = 0;
	while (true){
		if(c[x]!=c2[x]){return false;}
		x++;
		if(x>=len){break;}
	}
	return true;
}

