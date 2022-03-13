num_ls = list(map(int, list(input())))

bif = len(num_ls)//2

if (sum(num_ls[:bif]) == sum(num_ls[bif:])):
    print('LUCKY')
else:
    print('READY')