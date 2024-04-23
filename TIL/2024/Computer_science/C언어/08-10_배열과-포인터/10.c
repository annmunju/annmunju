#include <stdio.h>
void main(){
    static int a[ ] = {10, 20, 30, 40, 50};
    int *pt, b, c, d;
    pt = a;
    b = *pt + *(pt+3);
    pt++;
    c = *pt + *(pt+3);
    d = *pt + 3;
    printf("b=%d, c=%d, d=%d", b, c, d);
}