#include "libs/iso646.h"


void test(){
	int x = 5;
	int y = 'A';


	if(y<127 and (x>5 or x&1==1)){
		__debugScreen__(y);
		y++;
	}
}
