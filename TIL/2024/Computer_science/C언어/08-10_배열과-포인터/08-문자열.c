#include <stdio.h>
void main(){
    char string[50];
    int i=0;
    printf("문자열을 입력하세요: ");
    scanf("%s", string);
    printf("입력받은 문자열: %s\n", string);
    printf("문자 단위 출력: ");
    while(string[i] != "\0"){
        printf("%c", string[i]);
        i++;
    }
}