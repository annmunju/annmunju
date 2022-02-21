array = [7, 5, 9, 0, 3, 1, 6, 2, 4, 8]

def quickSort(array, start, end):
    if start >= end:
        return
    pivot = start
    left = start + 1
    right = end
    while left <= right:
        while left <= end and array[left] <= array[pivot]:
            left += 1
        while right > start and array[right] >= array[pivot]:
            right -= 1
        if left > right:
            array[right], array[pivot] = array[pivot], array[right]
        else :
            array[left], array[right] = array[right], array[left]
    quickSort(array, start, right - 1)
    quickSort(array, right + 1, end)

# quickSort(array, 0, len(array)-1)
# print(array)

def quickSort2(array):
    if len(array) <= 1:
        return array
    pivot = array[0]
    tail = array[1:]

    left = [x for x in tail if x <= pivot]
    right = [x for x in tail if x > pivot]

    return quickSort2(left) + [pivot] + quickSort2(right)

# print(quickSort2(array))

# ---

array = [1, 7, 8, 2, 8, 3, 4, 6, 1, 0, 5, 2]

count = [0] * (max(array)+1)

for i in range(len(array)):
    count[array[i]] += 1

for i in range(len(count)):
    for j in range(count[i]):
        print(i, end=' ')