import pandas as pd

# 读取Excel文件
df = pd.read_excel('data/20240330数据集.xlsx')

# 定义需要处理的列
columns_to_process = ['申请号', '公开（公告）号', '申请日', '公开（公告）日']

# 对每一列进行处理，只保留第一个值
for column in columns_to_process:
    df[column] = df[column].apply(lambda x: x.split(';')[0] if pd.notnull(x) else x)

# 保存处理后的数据到新的Excel文件
df.to_excel('data/20240330数据集_去重.xlsx', index=False)

print("处理完成，处理后的数据已保存到 'data/20240330数据集_去重.xlsx'")

#3107 / 5803