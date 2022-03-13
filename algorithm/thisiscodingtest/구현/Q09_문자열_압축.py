str_ls = input()
circle = 1

all_ls = list()

while circle <= len(str_ls) // 2:

    length = len(str_ls) // circle
    ls = []
    for i in range(length):
        ls.append(str_ls[circle*i:circle*(i+1)])

    all_ls.append(ls)
    circle += 1

for ls_idx in range(len(all_ls)):
    first_ls = all_ls[ls_idx]
    cnt = 1
    cnt_ls = []

    for i in range(len(first_ls)-1):
        if first_ls[i] == first_ls[i+1]:
            cnt += 1
        if first_ls[i] != first_ls[i+1]:
            cnt = 1
        cnt_ls.append(cnt)
    max_cnt = max(cnt_ls)
    print('인덱스 :',ls_idx+1,'최대 cnt :', max_cnt)
    if max_cnt > 1:
        print('인덱스와 최대cnt의 곱', (ls_idx+1) * max_cnt)
        result = (ls_idx + 1) * max_cnt
        print('결과 :',)