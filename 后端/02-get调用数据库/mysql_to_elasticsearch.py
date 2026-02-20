import csv
from elasticsearch import Elasticsearch


class ESCreateIndex:
    def __init__(self, index_name):
        # 连接到本地 Elasticsearch
        self.es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])
        self.index_name = index_name

    def create_index(self):
        # 如果索引已存在，则先删除
        if self.es.indices.exists(index=self.index_name):
            self.es.indices.delete(index=self.index_name)
            print("现有索引已删除。")

        # 创建新的索引
        self.es.indices.create(index=self.index_name)
        print("索引创建成功。")

    def insert_data(self, file_path):
        # 从 CSV 文件中读取数据
        with open(file_path, mode='r', encoding='utf-8-sig') as file:  # 注意这里改为 'utf-8-sig'
            reader = csv.DictReader(file)
            for row in reader:
                # 将 CSV 中的每行数据插入 Elasticsearch
                self.es.index(index=self.index_name, body={
                    "申请号": row['申请号'],
                    "公开号": row['公开号'],
                    "申请日": row['申请日'],
                    "公开日": row['公开日'],
                    "文献类型": row['文献类型'],
                    "名称": row['名称'],
                    "摘要": row['摘要']
                })
                print(f"已插入数据：{row['名称']}")

    def search_patent(self, query):
        # 执行搜索
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["名称", "摘要"]
                }
            }
        }
        response = self.es.search(index=self.index_name, body=body)
        return response

    def search_patent_name(self, query, page=1, page_size=10):
        from_ = (page - 1) * page_size
        # 执行搜索
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["名称^2", "摘要"]  # 提高“名称”字段的权重
                }
            },
            "highlight": {  # 添加高亮字段
                "fields": {
                    "名称": {},  # 高亮专利名称
                    "摘要": {}  # 同时高亮摘要
                },
                "pre_tags": ["<strong>"],  # 高亮标签前缀
                "post_tags": ["</strong>"]  # 高亮标签后缀
            },
            "from": from_,  # 指定开始位置
            "size": page_size  # 指定返回结果的数量
        }
        response = self.es.search(index=self.index_name, body=body)
        search_time = response.get('took', 0)  # 获取搜索用时
        total_results = response['hits']['total']['value']  # Elasticsearch返回的总结果数
        # 处理返回的数据，提取高亮结果
        results = []
        for hit in response['hits']['hits']:
            result = {
                "申请号": hit["_source"]["申请号"],
                "公开号": hit["_source"]["公开号"],
                "申请日": hit["_source"]["申请日"],
                "公开日": hit["_source"]["公开日"],
                "文献类型": hit["_source"]["文献类型"],
                "名称": hit["_source"]["名称"],
                "摘要": hit["_source"]["摘要"],
                "高亮": {
                    "名称": hit["highlight"]["名称"][0] if "名称" in hit["highlight"] else hit["_source"]["名称"],
                    "摘要": hit["highlight"]["摘要"][0] if "摘要" in hit["highlight"] else hit["_source"]["摘要"]
                }
            }
            results.append(result)
        return results, search_time,total_results


if __name__ == "__main__":
    es_index = ESCreateIndex("patent")
    es_index.create_index()
    es_index.insert_data("neo4j/data/index/实体-专利.csv")
    # 示例搜索
    # search_result = es_index.search_patent_name("隧道")
    # print(search_result)
