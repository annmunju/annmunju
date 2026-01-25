import cudf as pd_gpu

df = pd_gpu.read_csv('data/price_paid_records.csv')
print('시작')
print(df.head())
print('종료')