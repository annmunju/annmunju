N = int(input())
plan_ls = list(input().split())

# L, R, U, D 순서
x_ls = [0, 0, -1, 1]
y_ls = [-1, 1, 0, 0]
LRUD = ['L', 'R', 'U', 'D']

x, y = 1, 1
nx = 0
ny = 0

for plan in plan_ls:
    for i in range(len(LRUD)):
        if plan == LRUD[i]:
            nx = x + x_ls[i]
            ny = y + y_ls[i]

        if 0 < nx < N+1 and 0 < ny < N+1:
            x, y = nx, ny
        else :
            continue

print(x, y)

# for plan in plan_ls:
#     if plan == 'L':
#         new_myMap = [x+y for x,y in zip(myMap, x_y_ls[0])]
#         if 0 < new_myMap[0] < N+1 and 0 < new_myMap[1] < N+1:
#             myMap = new_myMap
#
#     elif plan == 'R':
#         new_myMap = [x+y for x,y in zip(myMap, x_y_ls[1])]
#         if 0 < new_myMap[0] < N + 1 and 0 < new_myMap[1] < N + 1:
#             myMap = new_myMap
#
#     elif plan == 'U':
#         new_myMap = [x+y for x,y in zip(myMap, x_y_ls[2])]
#         if 0 < new_myMap[0] < N + 1 and 0 < new_myMap[1] < N + 1:
#             myMap = new_myMap
#
#     elif plan == 'D':
#         myMap = [x+y for x,y in zip(myMap, x_y_ls[3])]
#         if 0 < new_myMap[0] < N + 1 and 0 < new_myMap[1] < N + 1:
#             myMap = new_myMap
#
# print(myMap[0], myMap[1])
