import time

n, m = map(int, input().split())
Ks = list(map(int, input().split()))

start_time = time.time()

cnt = 0
for i in range(n):
    if Ks[i] in list(Ks[i+1:]):
        cnt += (len(list(Ks[i+1:])) - Ks[i+1:].count(Ks[i]))
    else :
        cnt += len(list(Ks[i+1:]))

print(cnt)

print(time.time() - start_time)