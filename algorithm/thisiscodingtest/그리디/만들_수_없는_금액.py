N = int(input())
ls = list(map(int, input().split()))

ls.sort()

if ls[0] >= 1 :
    min = ls[0]-1

print(min)