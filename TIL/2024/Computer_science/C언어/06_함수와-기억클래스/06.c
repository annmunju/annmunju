#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

int sum(int a, int b);

int main(){
    double x=12.34;
    int i=-5,j=2;
    int a,b,c;
    a=ceil(x);
    b=floor(x);
    c=pow(4, j);
    printf("abs(-5)=%d\n", abs(i)); // 절댓값
    printf("ceil(12.34)=%d\n", a); // x 이상의 최소 정숫값
    printf("cos(10)=%f\n", cos(10)); // 코사인
    printf("exp(2)=%.f\n", exp(j)); // 지숫값
    printf("floor(12.34)=%d\n", b); // x 이하의 최대 정숫값
    printf("sqrt(2)=%5f\n", sqrt(j)); // 루트
    printf("pow(4,2)=%d\n", c); // 지수

    int ii, alp=0, no=0, et=0;
    char s[20];
    printf("문자");
    scanf("%s", s);
    for(i=0; i<strlen(s); i++){
        if(isalpha(s[i]))
            alp++;
        else if(isdigit(s[i]))
            no++;
        else
            et++;
    }
    printf("알파벳 = %d\n", alp);
    printf("숫자 = %d\n", no);
    printf("기타 = %d\n", et);

    printf("기타 제외 개수 = %d\n", sum(no, et));
}

int sum(int a, int b){
    int d;
    d=a+b;
    return(d);
}