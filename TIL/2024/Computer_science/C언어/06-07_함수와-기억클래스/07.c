#include <stdio.h>
void swap_1(int x, int y);
void swap_2(int *x, int *y);
void main(){
    int a=3, b=5;
    printf("호출전 a = %d, b = %d\n", a, b);
    swap_1(a, b);
    swap_2(&a, &b);
    printf("호출후 a = %d, b = %d\n", a, b);
}
void swap_1(int x, int y){
    int temp;
    temp = x;
    x = y;
    y = temp;
    printf("함수내 x = %d, y = %d\n", x, y);
} // 값에 의한 자료 전달
void swap_2(int *x, int *y){
    int temp;
    temp = *x;
    *x = *y;
    *y = temp;
    printf("함수내 x = %d, y = %d\n", *x, *y);
} // 참조에 의한 자료 전달