import pandas as pd

# 读取Excel文件
df = pd.read_excel('data/20240330数据集_去重.xlsx')

# 定义一个处理函数来分隔实体并去除空格
def split_and_strip(cell):
    if pd.notna(cell):
        # 分隔实体并去除前后空格
        entities = [entity.strip() for entity in cell.split(';')]
        # 去除重复实体
        return list(set(entities))
    return []

# 抽取“专利”实体
patents = df[['申请号', '公开（公告）号', '申请日', '公开（公告）日', '文献类型', '发明名称', '摘要']].copy()
patents.columns = ['申请号', '公开号', '申请日', '公开日', '文献类型', '名称', '摘要']
patents.to_csv('data/实体-专利.csv', index=False, encoding='utf_8_sig')

# 抽取“IPC”实体
ipc = df['IPC分类号'].str.split(';', expand=True).stack().str.strip().reset_index(level=1, drop=True).to_frame(name='名称')
ipc = ipc.drop_duplicates().reset_index(drop=True)
ipc.to_csv('data/实体-IPC.csv', index=False, encoding='utf_8_sig')

# 抽取“发明人”实体，确保去重和去除空格
df['发明人'] = df['发明人'].apply(split_and_strip)
inventors = pd.DataFrame(df['发明人'].explode().dropna().unique(), columns=['名称'])
inventors.to_csv('data/实体-发明人.csv', index=False, encoding='utf_8_sig')

# 抽取“申请人”实体
df['申请（专利权）人'] = df['申请（专利权）人'].apply(split_and_strip)
applicants = pd.DataFrame(df['申请（专利权）人'].explode().dropna().unique(), columns=['名称'])
# 申请人邮编不会被分割，每个申请人只有一个邮编
applicants['邮编'] = df['申请人邮编']
applicants = applicants.drop_duplicates().reset_index(drop=True)
applicants.to_csv('data/实体-申请人.csv', index=False, encoding='utf_8_sig')

# 抽取“代理机构”实体，并去除尾部可能的邮编
df['代理机构'] = df['代理机构'].str.replace(r'\s+\d+$', '', regex=True).str.strip()
agents = pd.DataFrame(df['代理机构'].dropna().unique(), columns=['名称'])
agents.to_csv('data/实体-代理机构.csv', index=False, encoding='utf_8_sig')

print("实体抽取完毕，文件已保存到data文件夹下。")
