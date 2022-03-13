N = input()
if len(N) == 2:
    N1, N0 = int(N[0])+1, int(N[1])+1
else :
    N1, N0 = 1, int(N)+1

cnt = 0

for h1 in range(N1):
    for h0 in range(N0):
        for m1 in range(6):
            for m0 in range(10):
                for s1 in range(6):
                    for s0 in range(10):
                        print([h1, h0, m1, m0, s1, s0])
                        if 3 in [h1, h0, m1, m0, s1, s0]:
                            cnt += 1

print(cnt)