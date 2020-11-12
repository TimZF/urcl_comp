void Main(){
    int a[3] = {1,2,3};
    int* pt = a;
    *(pt+1) = 5;
    //__debugInt__(*(pt+1));
    __debugInt__(sizeof(char));
}
