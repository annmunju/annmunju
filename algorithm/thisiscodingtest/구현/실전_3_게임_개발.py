# n(세로) X m(가로) 맵
n, m = map(int, input().split())
# 캐릭터 출발 위치 (a, b)와 방향 d
a, b, d = map(int, input().split())

game_map = list()

for _ in range(n):
    game_map.append(input().split())

# while True:
#     pass

# 왼쪽에 가보지 않은 칸이 존재한다면... (전진 좌표 a, b와 방향 d)
# d 가 0이면 move_ls[0]의 첫번째, 두번째 내용으로 작성된 이동경로를 받아 a는 -1칸, b는 0칸 이동함을 기록
move_ls = [(-1, 0, 3), (0, -1, 0), (1, 0, 1), (0, 1, 2)]
cnt = 0


while 0 <= a <= n and 0 <= b <= n:

    if game_map[a][b] == '0':
        # 이동 횟수 cnt 추가
        cnt += 1
        # 현재 위치에 나 왔던곳임! 표시 (1)
        game_map[a][b] = '1'
        # 이동 못한 횟수 초기화
        no_move = 0

    # 이동하게 될 경로를 a_move와 b_move에 받아놓고 판단해보자
    a_move = a + move_ls[d][0]
    b_move = b + move_ls[d][1]

    # 0으로 되어있으니까 이동 가능한 경우 -> a, b, d 업데이트!
    if game_map[a_move][b_move] == '0':
        a = a_move
        b = b_move
        d = move_ls[d][2]

    # 1로 되어있으니까 이동 불가한 경우 -> d(방향)만 업데이트!
    # no_move가 4번이면(다 돌았다는 거라) 뒤로 가야하니까 no_move도 하나 추가
    elif game_map[a_move][b_move] == '1':
        no_move += 1
        d = move_ls[d][2]

    # no_move가 4번이면(다 돌았다) 뒤로 빠질수 있는지 없는지 판단
    # 방향 1번 전환 후 전진인 move_ls 기록을 활용해서 방향 2번 전환 후 전진(즉 후진) 방향인 new_d를 생성
    if no_move == 4:
        new_d = move_ls[d][2]
        a_move = a + move_ls[new_d][0]
        b_move = b + move_ls[new_d][1]

        # 그럼 new_d 방향으로 전진 불가능하면 끝!
        if game_map[a_move][b_move] == '1':
            break

for map in game_map:
    for m in map:
        print(m, end=' ')
    print()

print(cnt)