#include "libs/malloc.c"
#include "libs/FS.c"
#include "libs/io.c"
#include "libs/string.c"

char stri1[] = "5678";
char stri2[] = "1234";

void main(){
	initMalloc();
	initFS();


	int file_id = create_file();
	int file_id2 = create_file();

	int len = strlen(stri1);

	int offset1 = writePart(file_id, 0, stri1, len);
	int offset2 = writePart(file_id2, 0, stri2, len);


	readPart(file_id,  0, stri2, len);
	readPart(file_id2, 0, stri1, len);

	printString(stri1);
	printString(stri2);

}
//load local into reg