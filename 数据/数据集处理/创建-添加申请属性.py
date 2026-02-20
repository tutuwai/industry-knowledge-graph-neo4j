from py2neo import Graph
import pandas as pd

# 连接到Neo4j数据库
url = 'bolt://localhost:7687'  # 假设你使用Bolt协议
user = 'neo4j'
password = 'CHW123d456'
graph = Graph(url, auth=(user, password))

# 读取CSV文件
data = pd.read_csv('data/实体-申请人-带省份.csv')

# 更新数据库中的Applicant节点
for index, row in data.iterrows():
    if pd.notna(row['Province']):  # 确保省份不是NaN
        query = """
        MATCH (a:Applicant {名称: $name})
        SET a.province = $province
        RETURN a
        """
        # 执行Cypher查询，更新省份属性
        graph.run(query, name=row['Name'], province=row['Province'])

print("省份属性已成功添加到Applicant实体中。")
