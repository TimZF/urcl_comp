#include "libs/malloc.c"
//#include "libs/virtualFS.c"
//#include "libs/fixedpoint.c"
#include "libs/io.c"


//char stri1[] = "\n/3=\n";
//char stri2[] = "\n*3=\n";

void main(){
	init();
	char* reg = malloc(10);
	itoa(34224, reg);
	printString(reg);
	__debugInt__(34224);
	__debugScreen__('\n');

	//int fileId1 = createFile(8);
	//int fileId2 = createFile(16);
	//int fileId3 = createFile(32);

	//rm(fileId2);

	//ls();

	//int size = getFileSize(fileId1);
	//__debugInt__(size);
}
//load local into reg