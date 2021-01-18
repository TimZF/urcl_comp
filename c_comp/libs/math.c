#define __MATH


void modulo_divide(int* divRes, int* modRes, int a, int b){
	__asm__(b, "MOV R2, R1");
	__asm__(a);
	__asm__("MOV R3, R2", "IMM R2, 0");
	__asm__("IMM $4, 1", "LSH $2, $2","LSH $1, $1","BRC +8","CMP $2, $3");
	__asm__("BRN +3", "SUB $2, $2, $3","INC $1, $1","LSH $4, $4");
	__asm__("BRC +4","BRA -9","INC $2, $2","BRA -8");

	__asm__("MOV R4, R1",divRes,"STORE R1, R4");


	__asm__("MOV $1, $2");
	__asm__("BRP +3");
	__asm__("NOT $2, $1");
	__asm__("INC $1, $2");
	__asm__("MOV R2, R1",modRes,"STORE R1, R2");
}




void divide(int* res, int a, int b){
	__asm__(b, "MOV R2, R1");
	__asm__(a);
	__asm__("MOV R3, R2", "IMM R2, 0");
	__asm__("IMM $4, 1", "LSH $2, $2","LSH $1, $1","BRC +8","CMP $2, $3");
	__asm__("BRN +3", "SUB $2, $2, $3","INC $1, $1","LSH $4, $4");
	__asm__("BRC +4","BRA -9","INC $2, $2","BRA -8");

	__asm__("MOV R2, R1",res,"STORE R1, R2");
}



void modulo(int* res, int a, int b){
	__asm__(b, "MOV R2, R1");
	__asm__(a);
	__asm__("MOV R3, R2", "IMM R2, 0");
	__asm__("IMM $4, 1", "LSH $2, $2","LSH $1, $1","BRC +8","CMP $2, $3");
	__asm__("BRN +3", "SUB $2, $2, $3","INC $1, $1","LSH $4, $4");
	__asm__("BRC +4","BRA -9","INC $2, $2","BRA -8");

	__asm__("MOV $1, $2");
	__asm__("BRP +3");
	__asm__("NOT $2, $1");
	__asm__("INC $1, $2");
	__asm__("MOV R2, R1",res,"STORE R1, R2");
}

