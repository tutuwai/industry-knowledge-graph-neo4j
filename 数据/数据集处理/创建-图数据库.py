import os
import csv
from py2neo import Graph, Node, Relationship


class PatentGraph:
    def __init__(self, url, user, password):
        # 当前文件所在目录
        cur_dir = os.path.dirname(__file__)
        # 实体节点文件路径
        self.patent_path = os.path.join(cur_dir, "data/实体-专利.csv")
        self.ipc_path = os.path.join(cur_dir, "data/实体-IPC.csv")
        self.agent_path = os.path.join(cur_dir, "data/实体-代理机构.csv")
        self.inventor_path = os.path.join(cur_dir, "data/实体-发明人.csv")
        self.applicant_path = os.path.join(cur_dir, "data/实体-申请人-带省份.csv")
        # 关系文件路径
        self.patent_patent_path = os.path.join(cur_dir, "data/关系-专利和专利.csv")
        self.patent_ipc_path = os.path.join(cur_dir, "data/关系-专利和IPC.csv")
        self.patent_agent_path = os.path.join(cur_dir, "data/关系-专利和代理机构.csv")
        self.patent_inventor_path = os.path.join(cur_dir, "data/关系-专利和发明人.csv")
        self.patent_applicant_path = os.path.join(cur_dir, "data/关系-专利和申请人.csv")

        # 连接Neo4j图数据库
        self.graph = Graph(url, user=user, password=password, name="neo4j")

    # 加载CSV文件并返回字典列表
    def load_csv(self, file_path):
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            return list(reader)

    # 创建节点
    def create_nodes(self, label, nodes):
        for node in nodes:
            properties = {k: v for k, v in node.items() if v not in ['', 'null', 'NULL']}
            self.graph.create(Node(label, **properties))
        print(f"Created {len(nodes)} '{label}' nodes.")

    # 创建关系-专利和其他四个关系的
    def create_relationships(self, file_path, start_label, end_label, rel_type):
        relationships = self.load_csv(file_path)
        for rel in relationships:
            p = rel['公开号'].strip()
            q = rel['名称'].strip()
            self.graph.run(
                f"MATCH (a:`{start_label}`), (b:`{end_label}`) "
                "WHERE a.公开号 = $start_node AND b.名称 = $end_node "
                f"CREATE (a)-[:`{rel_type}`]->(b)",
                parameters={
                    'start_node': p,
                    'end_node': q
                }
            )
        print(f"Created relationships from file '{file_path}'.")
        # 创建关系

    # 创建关系-专利和专利的
    def create_patent_relationships(self, file_path, start_label, end_label, rel_type):
        relationships = self.load_csv(file_path)
        for rel in relationships:
            p = rel['公开号'].strip()
            q = rel['被引用公开号'].strip()
            self.graph.run(
                f"MATCH (a:`{start_label}` {{公开号: $start_node}}), (b:`{end_label}` {{公开号: $end_node}}) "
                f"CREATE (a)-[:`{rel_type}`]->(b)",
                parameters={
                    'start_node': p,
                    'end_node': q
                }
            )
        print(f"Created relationships from file '{file_path}'.")
    # 构建整个图
    def build_graph(self):
        # 创建节点
        self.create_nodes('Patent', self.load_csv(self.patent_path))
        self.create_nodes('IPC', self.load_csv(self.ipc_path))
        self.create_nodes('Agent', self.load_csv(self.agent_path))
        self.create_nodes('Inventor', self.load_csv(self.inventor_path))
        self.create_nodes('Applicant', self.load_csv(self.applicant_path))
        #
        # # 创建关系
        self.create_relationships(self.patent_ipc_path, 'Patent', 'IPC', 'BELONGS_TO')
        self.create_relationships(self.patent_agent_path, 'Patent', 'Agent', 'REPRESENTED_BY')
        self.create_relationships(self.patent_inventor_path, 'Patent', 'Inventor', 'INVENTED_BY')
        self.create_relationships(self.patent_applicant_path, 'Patent', 'Applicant', 'APPLIED_BY')
        self.create_patent_relationships(self.patent_patent_path, 'Patent', 'Patent', 'CITES_BY')
    # 删除图中的所有节点和关系
    def delete_all(self):
        self.graph.delete_all()


# 实例化并运行
if __name__ == '__main__':
    url = 'http://localhost:7474/browser/'
    user = 'neo4j'
    password = 'CHW123d456'
    patent_graph = PatentGraph(url, user, password)

    # 如果需要清空现有数据库
    patent_graph.delete_all()

    # 使用新数据构建图
    patent_graph.build_graph()
