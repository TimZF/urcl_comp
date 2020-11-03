#define NULL 0
#define true 1
#define false 0


#include "libs/malloc.c"
#include "libs/io.c"
#include "libs/string.c"
#include "libs/arrayUtil.c"
#include "libs/iso646.h"
#include "libs/math.h"

char help_string[] = "HELP\nCALC\nCL\nP\nQ\n";
char commNotFound[] = "COMM\nNOT\nFOUND\nTRY\nHELP\n";
char helpComm[] = "HELP";
char calcComm[] = "CALC";
char clComm[] = "CL";
char startUp[] = "STARTING...\n";
char hw[] = "HELLO\nWORLD\n";









void calculator() {
	char *n1 = calloc(maxCharsOnScreen, 0);
	char *n2 = calloc(maxCharsOnScreen, 0);
	char *res = calloc(maxCharsOnScreen, 0);
	char a[] = "ENTER\nNUMBER 1\n>";
	char b[] = "\nENTER\nNUMBER 2\n>";
	printString(a);
	input(n1);
	printString(b);
	input(n2);

	int intN1 = atoi(n1);
	int intN2 = atoi(n2);
	__debugInt__(intN1);
	__debugInt__(intN2);
	itoa(intN1+intN2, res);
	__debugScreen__('\n');
	printString(res);
	__debugScreen__('\n');
}




void test(){
	int foundComm = 0;

	init();
	clear_screen();

	printString(startUp);

	int comm = calloc(maxCharsOnScreen, 0);
	int nChars = 0;
	printchar('>');

	while(true){
		input(comm);
		printchar(10);
		__debugChar__(comm[0]);
		__debugChar__(comm[1]);


		if(comm[0]=='Q'){
			return;
		}
		if(comm[0]=='P'){
			printString(hw);
			foundComm = 1;
		}
		if(strCmp(comm, clComm)==1){
			clear_screen();
			foundComm = 1;
		}
		if(strCmp(comm, helpComm)==1){
			printString(help_string);
			foundComm = 1;
		}
		if(strCmp(comm, calcComm)==1){
			calculator();
			foundComm = 1;
		}

		for(;nChars!=0;nChars--){
			comm[nChars] = 0;
			foundComm = 1;
		}

		if(foundComm == 0){printString(commNotFound);}

		printchar('>');
	}

}
