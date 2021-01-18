#include "./libs/malloc.c"

struct vec3
{
	int x;
	int y;
	int z;
};




void main() {
	//initMalloc();

	int a = 5;
	
	{
		int b = 4;
		{
			int c = 3;
			{
				int d = a;
			}
		}
	}
}
