N = int(input())
ls = list(map(int, input().split()))

ls.sort()

if ls[0] > 1:
    min = 1
else :
    i = 1
    min = ls[i-1] + 1
    while i < N:
        if min >= ls[i]:
            i += 1
            min += ls[i-1]
        else :
            break

print(min)