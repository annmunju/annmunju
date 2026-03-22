#include <stdio.h>
void main(){
    int days=365;
    int month=12;
    int Table[5]={1,2,3,4,5};
    // printf("days의 주소는 %x\n", &days);
    // printf("month의 주소는 %x\n", &month);
    // printf("배열명 Table의 주소는 %x\n", Table);
    // printf("배열명 Table 첫번째 요소의 주소는 %x\n", &Table[0]);
    // printf("배열명 Table 두번째 요소의 주소는 %x\n", &Table[1]);

    int a, b;
    int *p;
    a=5000;
    p=&a;
    b=*p;
    printf("%d\n", a);
    printf("%x\n", p);
    printf("%x\n", *p);
    printf("%x\n", b);

    int *x, y[ ]={10,20,30,40,50};
    x=&y[0];
    printf("*x == %d\n", *x);
    printf("*x++ == %d\n", *x++); // 포인트 값을 출력한 후 주소를 증가
    printf("*++x == %d\n", *++x); // 주소를 증가 후 출력
    x = x+2;
    printf("*x == %d\n", *x);
    printf("y[2] == %d\n", y[2]);
    printf("*x+2 == %d\n", *p+2); // 포인터 값에 2를 더함
}