array = [7, 5, 9, 0, 3, 1, 6, 2, 4, 8]

def choiceFunc(ls) :

    for i in range(len(ls)):
        min_index = i
        for j in range(i+1, len(ls)):
            if ls[min_index] > ls[j]:
                min_index = j
        ls[i], ls[min_index] = ls[min_index], ls[i]

    return ls

print(choiceFunc(array))

# 시간복잡도 : O(N^2)

def insertionFunc(ls):

    for i in range(1,len(ls)):
        for j in range(i, 0, -1):
            if ls[j] < ls[j-1]:
                ls[j], ls[j-1] = ls[j-1], ls[j]
            else :
                break

    return ls

print(insertionFunc(array))

# 시간복잡도 : O(N^2) 이지만 어느정도 정렬되어 있는 상황이냐에 따라 속도가 빨라짐.
