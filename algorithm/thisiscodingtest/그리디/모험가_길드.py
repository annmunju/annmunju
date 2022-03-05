N = int(input())
X = list(map(int,input().split()))

# 내림차순으로 정렬
X.sort(reverse=True)
i, cnt = 0, 0

while i < len(X):
    cnt += 1
    i += X[i]

print(cnt)