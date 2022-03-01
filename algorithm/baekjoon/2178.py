n, m = map(int, input().split())
graph = list()
for i in range(n):
    graph.append(list(map(int, list(input()))))

print(n, m, graph)

cnt = 0
x, y = 0, 0

while x >= 0 and x < n and y >= 0 and y < m:
    if graph[x][y] == 0:
        cnt += 1
        if graph[x+1][y] == 0:
            x += 1
        elif graph[x][y+1] == 0:
            y += 1
        elif graph[x-1][y] == 0:
            x -= 1
        elif graph[x][y-1] == 0:
            y -= 1

print(cnt)