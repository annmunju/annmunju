n, k = map(int, input().split())
a = list(map(int, input().split()))
b = list(map(int, input().split()))

def quickSort(array):
    if len(array) <= 1:
        return array
    pivot = array[0]
    tail = array[1:]

    left = [x for x in tail if x <= pivot]
    right = [x for x in tail if x > pivot]

    return quickSort(left) + [pivot] + quickSort(right)

a = quickSort(a)
b = quickSort(b)

for i in range(k):
    if a[i] < b[n-1-i]:
        a[i], b[n-1-i] = b[n-1-i], a[i]
    else :
        break

print(a)
print(b)
print(sum(a))