N, M = list(map(int, input().split()))
ls = list()

for _ in range(N):
    newLs = sorted(list(map(int, input().split())))
    ls.append(newLs[0])

print(max(ls))

# sorted 대신 min 함수 쓰면 시간복잡도가 O(NlogN) -> O(N)으로 감소함...