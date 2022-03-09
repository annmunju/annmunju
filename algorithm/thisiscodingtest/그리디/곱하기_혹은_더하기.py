S = [int(s) for s in input()]

result = S[0]

for s in S[1:]:
    if result*s == 0 or s == 1 or result == 1:
        result += s
    else :
        result *= s

print(result)

