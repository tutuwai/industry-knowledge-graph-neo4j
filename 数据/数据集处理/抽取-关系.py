import pandas as pd

# 读取Excel文件
df = pd.read_excel('data/20240330数据集_去重.xlsx')

# 定义一个函数来处理实体的分割和去重，并移除名称中的数字
def split_entities(entities):
    if pd.notna(entities):
        # 分割实体并去除尾部可能的数字和空格
        entities = [entity.strip() for entity in entities.split(';')]
        entities_cleaned = [entity for entity in entities if entity and entity.strip() != '']
        return list(set([entity for entity in entities_cleaned]))
    return []

# 函数来创建三元组关系，确保所有元素都是三元组
def create_relation_tuples(df, column, relation_name):
    relation_tuples = df.apply(lambda row: [(row['公开（公告）号'], entity, relation_name)
                                            for entity in split_entities(row[column])],
                               axis=1).explode().dropna().tolist()
    # 过滤掉None值
    relation_tuples = [i for i in relation_tuples if i is not None]
    return relation_tuples

# 为代理机构处理，确保去除名称中的数字
df['代理机构'] = df['代理机构'].str.replace(r'\s+\d+$', '', regex=True).str.strip()

# 生成发明人与专利之间的关系三元组
inventor_relations = create_relation_tuples(df, '发明人', '发明')
inventor_relations_df = pd.DataFrame(inventor_relations, columns=['公开号', '名称', '关系'])
inventor_relations_df.to_csv('data/关系-专利和发明人.csv', index=False, encoding='utf_8_sig')

# 生成代理机构与专利之间的关系三元组
agent_relations = create_relation_tuples(df, '代理机构', '代理')
agent_relations_df = pd.DataFrame(agent_relations, columns=['公开号', '名称', '关系'])
agent_relations_df.to_csv('data/关系-专利和代理机构.csv', index=False, encoding='utf_8_sig')

# 生成申请人与专利之间的关系三元组
applicant_relations = create_relation_tuples(df, '申请（专利权）人', '申请')
applicant_relations_df = pd.DataFrame(applicant_relations, columns=['公开号', '名称', '关系'])
applicant_relations_df.to_csv('data/关系-专利和申请人.csv', index=False, encoding='utf_8_sig')

# 生成专利与IPC之间的关系三元组
ipc_relations = create_relation_tuples(df, 'IPC分类号', '属于')
ipc_relations_df = pd.DataFrame(ipc_relations, columns=['公开号', '名称', '关系'])
ipc_relations_df.to_csv('data/关系-专利和IPC.csv', index=False, encoding='utf_8_sig')

print("关系数据抽取完毕，文件已保存到data文件夹下。")
