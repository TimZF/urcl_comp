
#define maxAddress 16380
#define maxHeapSize 10000

int* head;

void init(){
	//size,next,prev,free
	head = maxAddress;
	head[0] = maxHeapSize;
	head[1] = 0;
	head[2] = 0;
	head[3] = 1;
}

int* malloc(int size){
	int *block;
	block = head;
	while(1==1){
		if (block[3]==1) {if (block[0]>size) {break;}}

		if(block[1]==0){return 0;}
	
		block = block[1];
	}

	int* newBlock;
	newBlock = block-size-4;

	newBlock[0] = block[0]-size-4;
	newBlock[1] = 0;
	newBlock[2] = block;
	newBlock[3] = 1;

	block[0] = size;
	block[1] = newBlock;
	block[3] = 0;
	
	return newBlock+4;
}



int* calloc(int size, int initVal){
	int *block;
	block = head;
	while(1==1){
		if (block[3]==1) {if (block[0]>size) {break;}}

		if(block[1]==0){return 0;}
	
		block = block[1];
	}

	int* newBlock;
	newBlock = block-size-4;

	newBlock[0] = block[0]-size-4;
	newBlock[1] = 0;
	newBlock[2] = block;
	newBlock[3] = 1;

	block[0] = size;
	block[1] = newBlock;
	block[3] = 0;

	int startAddress = newBlock+4;
	for(int x = 0; x<size; x++){
		startAddress[x] = initVal;
	}

	
	return newBlock+4;
}













void free(int *posi){
	posi = posi[-2];
	posi[3] = 1;
	cleanUp();
}

void cleanUp(){
	int *block;
	int *m;
	block = head;
	//seach if theres a block and the next block is blocked and then merge them
	while(block!=0){
		if(block[3]==1){
			m = block[1];
			if(m[3]==1){
				block[0] = block[0]+m[0]+4;
				block[1] = m[1];
				block = block[2];
			}
		}
		block = block[1];
	}
}

int* realloc(int *posi, int newSize){
	posi = posi[-2];
	if(posi[0]>newSize){posi = posi[1];return posi+4;}

	//free old
	posi[3] = 1;
	cleanUp();
	//alloc new size
	return malloc(newSize);
}






/*
test2(int *arr, int size){
	__debugInt__(size);
	for(int x=0;x<size;x++){
		arr[x] = x+1;
		__debugInt__(x);
	}
}


test()
{
	init();
	int *allocatedStuff = malloc(5);
	__asm__("HLT");

	int *allocatedStuff2 = malloc(5);
	__asm__("HLT");

	int *allocatedStuff = realloc(allocatedStuff, 10);
}*/
