import pandas as pd

# 读取数据
entities = pd.read_csv('data/实体-专利.csv')
relations_pre = pd.read_csv('data/关系-专利和专利-处理前.csv')

# 获取实体中所有的公开号
public_ids = set(entities['公开号'])

# 过滤关系，确保关系中的公开号都存在于实体的公开号集合中，并且排除自引用的情况
filtered_relations = relations_pre[
    (relations_pre['公开号'].isin(public_ids)) &
    (relations_pre['被引用公开号'].isin(public_ids)) &
    (relations_pre['公开号'] != relations_pre['被引用公开号'])
]

# 进行去重操作
filtered_relations = filtered_relations.drop_duplicates()

# 保存过滤和去重后的结果到新的CSV文件
filtered_relations.to_csv('data/关系-专利和专利.csv', index=False)

print("过滤和保存完成。")
