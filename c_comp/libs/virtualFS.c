#ifndef maxHeapSize
#include "malloc.c"
#endif
#ifndef maxCharsOnScreen
#include "io.c"
#endif
#ifndef __STRING
#include "string.c"
#endif

int fadd[16] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}; //16 file locations
int fsize[16] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}; //16 file locations

char lsPrint[] = "FILEID SIZE\n";

void ls(){
	printString(lsPrint);
	char* numberSpace = malloc(4);
	for(int x = 0;x<16;x++){
		if (fadd[x]!=0){
			itoa(x, numberSpace);
			printString(numberSpace);
			__debugScreen__(32);
			itoa(fsize[x], numberSpace);
			printString(numberSpace);
			__debugScreen__(10);
			//print file info
		}
	}
}

int getFileSize(int fileId){
	return fsize[fileId];
}

void rm(int fileId){
	free(fadd[fileId]);
	fadd[fileId] = 0;
	fsize[fileId] = 0;
}

int createFile(int size){
	int fileIdGot = 0;
	while(fadd[fileIdGot]!=0){
		fileIdGot = fileIdGot+1;
		if(fileIdGot>15){return 100;}
	}
	fadd[fileIdGot] = calloc(size, 0);
	fsize[fileIdGot] = size;
	return fileIdGot;
}

void resizeFile(int fileId, int newSize){
	fadd[fileId] = realloc(fadd[fileId], newSize);
	fsize[fileId] = newSize;
}

void writeToFile(int fileId, char* data){
	int len = 0;
	while(1){
		if(data[len]==0){break;}
		len = len + 1;
	}
	if(len>=fsize[fileId]){
		resizeFile(fileId, len+1);
	}

	char* filePtr = fadd[fileId];
	len = 0;
	while(1){
		filePtr[len] = data[len];
		if(data[len]==0){break;}
		len = len+1;
	}	
}

char* readFromFile(int fileId){
	char* out = malloc(fsize[fileId]);
	char* filePtr = fadd[fileId];
	int x = 0;
	while(1){
		out[x] = filePtr[x];
		if(filePtr[x]==0){break;}
		x = x+1;
	}
	return out;
}
