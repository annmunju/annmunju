## DFS

def dfs(graph, v, visited):
    # 현재 노드 방문처리
    visited[v] = True
    print(v, end=' ')
    # 현재 노드와 연결된 다른 노드를 재귀적으로 방문
    for i in graph[v]:
        if not visited[i]:
            dfs(graph, i, visited)

graph = [
    [],
    [2, 3, 8], #1과 연결된
    [1, 7], #2와 연결된
    [1, 4, 5], #3과 연결된
    [3, 5], #4와 연결된
    [3, 4], #5와 연결된
    [7],
    [2, 6, 8],
    [1, 7]
]

# 각 노드의 방문 정보
visited = [False] * 9

dfs(graph, 1, visited)

## BFS

from collections import deque

def bfs(graph, start, visited):
    # 큐 구현을 위한 라이브러리 사용
    queue = deque([start])
    # 현재 노드 방문처리
    visited[start] = True
    # 큐가 빌 때까지 반복
    while queue:
        v = queue.popleft()
        print(v, end=' ')
        # 아직 방문하지 않은 인접한 원소들을 큐에 삽입
        for i in graph[v]:
            if not visited[i]:
                queue.append(i)
                visited[i] = True

visited = [False] * 9
print()
bfs(graph, 1, visited)