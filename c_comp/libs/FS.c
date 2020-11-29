//x=64;int((16384-244*2)/(x+1));16384-(int((16384-244*2)/(x+1))*(x+1)+244*2)
//blockSize = 64; last one has next pointer and sign bit if free
//244 maxnFiles
//10 
#define memSize 16384
#define blockSize 64
#define maxNFiles 244
#define fileSizeTable 0
#define fileAddrTable maxNFiles
#define startOfData maxNFiles+maxNFiles


void initFS(){
	int x = 0;
	for(; x<maxNFiles; x++){
		__asm__(fileSizeTable+x, "OUT 120, R1");
		__asm__("OUT 124, 0");
	}
	x = 0;
	for(; x<maxNFiles; x++){
		__asm__(fileAddrTable+x, "OUT 120, R1");
		__asm__("OUT 124, 0");
	}
}


void writeArr(int addr, int* arr, int len){
	for(int x = 0; x<len; x++){
		__asm__(addr+x,"OUT 120, R1");
		__asm__(arr[x],"OUT 124, R1");
	}
}

void updateFileInfo(int fileId, int size, int addr){
	__asm__(fileSizeTable+fileId,"OUT 120, R1");
	__asm__(size,"OUT 124, R1");

	__asm__(fileAddrTable+fileId,"OUT 120, R1");
	__asm__(addr,"OUT 124, R1");

}



int readAddr(int addr){
	int outVal = 0;
	__asm__(addr,"OUT 120, R1");
	__asm__(&outVal, "MOV R3, R1", "IN R1, 124", "STORE, R3, R1");
	return outVal;
}

void writeAddr(int addr, int val){
	__asm__(addr,"OUT 120, R1");
	__asm__(val, "OUT 124, R1");
}

int getOpenBlock(){
	for(int x = startOfData; x<memSize; x = x+blockSize+1){
		if(readAddr(x)>=0){return x;}
	}
}


int writePart(int fileId, int offset, int* data, int len){//writes len into existing file and returns next offset
	int fileAddr = readAddr(fileAddrTable+fileId);
	int x=0;
	for(; x<offset; x++){
		fileAddr = readAddr(fileAddr);
	}
	x=0;
	for(; x<len; x++){
		writeAddr(fileAddr+x+1, data[x]);
	}
	return offset+1;
}

int readPart(int fileId, int offset, int* data, int len){//reads len into data and returns next offset
	int* fileAddr = readAddr(fileAddrTable+fileId);
	int* newFileAddr;
	int x=0;
	for(; x<offset; x++){
		fileAddr = readAddr(fileAddr);
	}
	x=0;
	for(; x<len; x++){
		data[x] = readAddr(fileAddr+x+1);
	}
	return offset+1;
}



int write(int fileId, int offset, int* data){//writes 64 into existing file and returns new offset
	int fileAddr = readAddr(fileAddrTable+fileId);
	int x=0;
	for(; x<offset; x++){
		fileAddr = readAddr(fileAddr);
	}
	x=0;
	for(; x<blockSize; x++){
		writeAddr(fileAddr+x+1, data[x]);
	}
	return offset+1;
}

int read(int fileId, int offset, int* data){//reads 64 into data and returns offset
	int* fileAddr = readAddr(fileAddrTable+fileId);
	int* newFileAddr;
	int x=0;
	for(; x<offset; x++){
		fileAddr = readAddr(fileAddr);
	}
	x=0;
	for(; x<blockSize; x++){
		data[x] = readAddr(fileAddr+x+1);
	}
	return offset+1;
}


int create_file(){//create file and alloc first block and reutrns fileId
	int fileId = 0;
	for(int x=0; x<maxNFiles; x++){
		fileId = readAddr(x);
		if (fileId==0){
			fileId=x;
			break;
		}
	}
	int* newBlock = getOpenBlock();
	writeAddr(newBlock, (1<<15 | 0));
	updateFileInfo(fileId, 1, newBlock);
}




void append(int fileId, int* data){//appends 64 to existing file
	int fileAddr = readAddr(fileAddrTable+fileId);
	int fileSize = readAddr(fileId)-1;
	int x=0;
	for(; x<fileSize; x++){
		fileAddr = readAddr(fileAddr);
	}

	int* newBlock = getOpenBlock();
	if(newBlock==0){return;}
	writeAddr(fileAddr, (1<<15 | newBlock));
	writeAddr(newBlock, (1<<15 | 0));

	x=0;
	for(; x<blockSize; x++){
		writeAddr(newBlock+x+1, data[x]);
	}
}


void ls(){

}

void delete(int fileId){
	int* fileAddr = readAddr(fileAddrTable+fileId);
	int fileSize = readAddr(fileId)-1;
	int* newFileAddr;
	for(int x=0; x<fileSize; x++){
		newFileAddr = readAddr(fileAddr);
		writeAddr(fileAddr,0);
		fileAddr = newFileAddr;
	}
	updateFileInfo(fileId, 0, 0);
}
