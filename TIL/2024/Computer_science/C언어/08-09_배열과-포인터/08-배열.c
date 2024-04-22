#include <stdio.h>
void main(){
    int array1[4]={10,20,30,40};
    int array2[ ]={10,20,30,40};
    int array3[4]={10,20};
    int array4[4]={0};

    static int x[ ]={1,2,3,4};
    static int y[ ]={10,20,30,40};
    
    int i;
    for(i=0; i<=3; i++)
        printf("array1[%d]=%d \t", i, array1[i]);
    printf("\n");

    for(i=0; i<=3; i++)
        printf("array2[%d]=%d \t", i, array2[i]);
    printf("\n");

    for(i=0; i<=3; i++)
        printf("array3[%d]=%d \t", i, array3[i]);
    printf("\n");

    for(i=0; i<=3; i++)
        printf("array4[%d]=%d \t", i, array4[i]);
    printf("\n");

    int j, z[4];
    for(j=0; j<4; ++j)
        z[j] = x[j] + y[3-j];
    printf("반대 위치 배열요소 합\n");
    for(j=0; j<4; ++j)
        printf("%d + %d = %d\n", x[j], y[3-j], z[j]);
}