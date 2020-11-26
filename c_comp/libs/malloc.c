#define size_t int
#define maxAddress 16380
#define maxHeapSize 10000


struct mallocStruct
{
	int size;
	int* next;
	int* prev;
	int free;
};

#define mallocStruct struct mallocStruct


mallocStruct* head;

void init(){
	//size,next,prev,free
	head = maxAddress;

	head->size = maxHeapSize;
	head->next = 0;
	head->prev = 0;
	head->free = 1;
}

int* malloc(size_t size){
	if(size<=0){return 0;}
	mallocStruct* block;
	block = head;
	while(1==1){
		if (block->free==1) {if (block->size>=size) {break;}}

		if(block->next==0){return 0;}
	
		block = block->next;
	}

	mallocStruct* newBlock;
	newBlock = block-size-4;

	newBlock->size = block->size-size-4;
	newBlock->next = 0;
	newBlock->prev = block;
	newBlock->free = 1;

	block->size = size;
	block->next = newBlock;
	block->free = 0;
	
	return newBlock+4;
}


int* calloc(size_t size, int initVal){
	if(size<=0){return 0;}
	mallocStruct* block;
	block = head;

	while(1==1){
		if (block->free==1) {if (block->size>=size) {break;}}

		if(block->next==0){return 0;}
	
		block = block->next;
	}

	mallocStruct* newBlock;
	newBlock = block-size-4;

	newBlock->size = block->size-size-4;
	newBlock->next = 0;
	newBlock->prev = block;
	newBlock->free = 1;

	block->size = size;
	block->next = newBlock;
	block->free = 0;

	int startAddress = newBlock+4;
	for(int x = 0; x<size; x++){
		startAddress[x] = initVal;
	}
	
	return newBlock+4;
}




void free(mallocStruct* posi){
	posi = posi[-2];
	posi->free = 1;
	cleanUp();
}

void cleanUp(){
	mallocStruct* block;
	mallocStruct* m;
	block = head;
	//seach if theres block free with a following block free and then merge them
	while(block!=0){
		if(block->free==1){
			m = block->next;
			if(m->free==1){
				block->size = block->size+m->size+4;
				block->next = m->next;
				block = block->prev;
			}
		}
		block = block->next;
	}
}

int* realloc(mallocStruct* posi, size_t newSize){
	if(newSize<=0){return 0;}
	posi = posi[-2];
	if(posi->size>newSize){posi = posi->next;return posi+4;}

	//free old
	posi->free = 1;
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
