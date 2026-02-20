import csv
from py2neo import Graph
from datetime import datetime

# 数据库连接配置
url = "bolt://localhost:7687"  # 确保使用正确的协议和端口
user = "neo4j"
password = "CHW123d456"

# 创建连接
graph = Graph(url, user=user, password=password)


# 执行查询并收集数据的函数
def fetch_data():
    years = range(2004, 2025)  # 从2004年到2024年
    results = []

    # 更新 fetch_data 函数中的年份循环和日期格式
    for year in years:
        # 对于每个年份，修改查询语句中的年份，统计截止到当前年份的数量
        query_patents = """
        MATCH (p:Patent)
        WHERE p.公开日 < '{end_year}.01.01'
        RETURN count(p) AS patent_count
        """.format(end_year=year + 1)

        query_relations = """
        MATCH (p:Patent)-[r]->(n)
        WHERE p.公开日 < '{end_year}.01.01' AND type(r) IN ['INVENTED_BY', 'BELONGS_TO', 'APPLIED_BY', 'REPRESENTED_BY', 'CITES_BY']
        RETURN type(r) AS relation_type, count(r) AS count
        """.format(end_year=year + 1)

        print(query_patents)
        print(query_relations)

        patent_count_result = graph.run(query_patents).evaluate()
        relation_results = graph.run(query_relations)

        count_dict = {
            '专利': patent_count_result,
            '专利与发明人': 0,
            '专利与ipc': 0,
            '专利与申请人': 0,
            '专利与代理机构': 0,
            '专利与专利': 0
        }

        for row in relation_results:
            relation = row['relation_type']
            relation = relation.replace('INVENTED_BY', '专利与发明人').replace('BELONGS_TO', '专利与ipc').replace(
                'APPLIED_BY', '专利与申请人').replace('REPRESENTED_BY', '专利与代理机构').replace('CITES_BY',
                                                                                                  '专利与专利')
            count_dict[relation] += row['count']

        results.append(count_dict)

    return results


# 保存结果到文本文件
def save_results(data):
    with open('data/时间数据统计.txt', 'w', newline='') as file:
        writer = csv.writer(file)
        headers = ['专利', '专利与发明人', '专利与ipc', '专利与申请人', '专利与代理机构', '专利与专利']
        writer.writerow(headers)
        for row in data:
            writer.writerow([row.get(h, 0) for h in headers])


# 主执行逻辑
if __name__ == '__main__':
    data = fetch_data()
    save_results(data)
    print("数据已保存到 data/时间数据统计.txt")
