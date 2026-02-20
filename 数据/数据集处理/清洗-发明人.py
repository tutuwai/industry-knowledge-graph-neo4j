import pandas as pd

# 读取发明人数据
inventors = pd.read_csv('data/实体-发明人.csv')

# 过滤掉名称中包含不规范数据的行，比如包含括号或特定字符串
filtered_inventors = inventors[
    ~inventors['名称'].str.contains(r'\(.*?\)|姓名', na=False)
]

# 保存过滤后的结果到新的CSV文件
filtered_inventors.to_csv('data/实体-发明人.csv', index=False)

print("已经成功删除包含特定字符串的数据。")
