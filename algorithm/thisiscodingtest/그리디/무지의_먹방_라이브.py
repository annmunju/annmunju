food_times = [3, 1, 2]
k = 5

length = len(food_times)
sum_times = sum(food_times)


if sum_times <= k:
    result = -1

else:
    while k != 0:
        ls = list()

        for idx, t in enumerate(food_times):
            if k == 0:
                break

            if t >= 1:
                ls.append(t-1)
                k -= 1
                print(ls, idx)
            elif t == 0:
                ls.append(0)
                print(ls, idx)

        compare_food_times = food_times
        food_times = ls

    print(compare_food_times, food_times, idx)
