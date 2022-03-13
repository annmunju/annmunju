loc = input()
# print(ord(loc[0])-96, loc[1])

x = int(loc[1])
y = ord(loc[0])-96

# 이동 경로 전체 (8가지)
# 위오, 위왼, 아래오, 아래왼,
# 우측이동후 왼쪽, 우측이동후 오른쪽, 좌측이동후 왼쪽, 좌측이동후 오른쪽
x_move = [-2, -2, 2, 2, -1, 1, 1, -1]
y_move = [1, -1, -1, 1, 2, 2, -2, -2]

cnt = 0

for i in range(8):
    mx = x + x_move[i]
    my = y + y_move[i]

    if 0 < mx < 9 and 0 < my < 9:
        cnt += 1

print(cnt)