S = list(input())

nums, ls_str = 0, list()

for s in S:
    if ord('A') <= ord(s):
        ls_str.append(s)
    else :
        s = int(s)
        nums += s

strs = ''.join(sorted(ls_str))

print(strs+str(nums))