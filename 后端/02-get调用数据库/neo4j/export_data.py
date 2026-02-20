from py2neo import Graph
import os
import json
from datetime import datetime
import csv


class Neo4jQuery:

    def __init__(self, url, user, password):
        self.graph = Graph(url, user=user, password=password, name="neo4j")
        # 规定返回的格式
        self.search_return = {
            '专利': "RETURN n, id(n)",
            '代理机构': "RETURN n, id(n)",
            '发明人': "RETURN n, id(n)",
            'IPC': "RETURN n, id(n)",
            '申请人': "RETURN n, id(n)",
            '专利与专利': "RETURN n.公开号 as from,m.公开号 as to,id(n) as id_from,id(m) as id_to,type(r) as rel",
            '专利与申请人': "RETURN n.公开号 as from,m.名称 as to,id(n) as id_from,id(m) as id_to,type(r) as rel",
            '专利与IPC': "RETURN n.公开号 as from,m.名称 as to,id(n) as id_from,id(m) as id_to,type(r) as rel",
            '专利与发明人': "RETURN n.公开号 as from,m.名称 as to,id(n) as id_from,id(m) as id_to,type(r) as rel",
            '专利与代理机构': "RETURN n.公开号 as from,m.名称 as to,id(n) as id_from,id(m) as id_to,type(r) as rel"
        }
        self.search_match = {
            '专利': "MATCH (n:Patent) ",
            '代理机构': "MATCH (n:Agent) ",
            '发明人': "MATCH (n:Inventor) ",
            'IPC': "MATCH (n:IPC) ",
            '申请人': "MATCH (n:Applicant) ",
            '专利与专利': "MATCH p = (n:Patent)-[r]->(m:Patent) ",
            '专利与申请人': "MATCH p = (n:Patent)-[r]->(m:Applicant) ",
            '专利与IPC': "MATCH p = (n:Patent)-[r]->(m:IPC) ",
            '专利与发明人': "MATCH p = (n:Patent)-[r]->(m:Inventor) ",
            '专利与代理机构': "MATCH p = (n:Patent)-[r]->(m:Agent) "
        }
        self.search_label = {
            '专利': "Patent",
            '代理机构': "Agent",
            '发明人': "Inventor",
            'IPC': "IPC",
            '申请人': "Applicant"
        }

    '''查找实体'''
    '''功能:根据pageRankScore阈值筛选实体,筛选出高于该值的实体'''
    '''
    参数:
        "label": "实体类型"
        "score_threshold"="得分值",
    返回:
        成功:返回查询结果的数组
        失败:返回Flase
    '''

    def search_entities(self, label=None, score_threshold=None):
        if label is None or score_threshold is None:
            return False

        query = f"{self.search_match[label]}WHERE n.pageRankScore >= {score_threshold} {self.search_return[label]}"
        print(query)

        try:
            nodes = self.graph.run(query)
            result = []
            for node in nodes:
                properties = dict(node["n"])
                properties["type"] = label
                properties["id"] = node["id(n)"]
                result.append(properties)
            return result
        except Exception as e:
            print(f"查询失败: {e}")
            return False

    '''查找关系'''
    '''功能:根据关系两端的pageRankScore阈值筛选关系,筛选出高于该值的关系'''
    '''
    参数:
        "rel_type": "关系类型"
        "property_key"="关系属性名称",
        "from_score_threshold"="值"
        "to_score_threshold"="值"
    返回:
        查询结果的数组
    '''

    def search_relationships(self, rel_type=None, from_score_threshold=None, to_score_threshold=None):
        if rel_type is None or from_score_threshold is None or to_score_threshold is None:
            return False

        query = f"{self.search_match[rel_type]}WHERE n.pageRankScore >= {from_score_threshold} AND m.pageRankScore >= {to_score_threshold} {self.search_return[rel_type]}"
        print(query)

        try:
            relationships = self.graph.run(query)
            result = []
            for rel in relationships:
                properties = dict(rel)
                properties["from_type"] = rel_type.split('与')[0]
                properties["to_type"] = rel_type.split('与')[1]
                result.append(properties)
            return result
        except Exception as e:
            print(f"查询失败: {e}")
            return False

    def search_time(self, label, start_time, end_time, time_property="公开日"):
        query = f"MATCH (n:{label}) WHERE n.{time_property} >= '{start_time}' AND n.{time_property} <= '{end_time}' RETURN n, id(n) as nodeId"
        try:
            nodes = self.graph.run(query)
            result = [{'id': node['nodeId'], 'properties': dict(node['n'])} for node in nodes]
            return result
        except Exception as e:
            print(f"按时间查询失败: {e}")
            return False

    # 宏观接口查询
    def get_filtered_data(self, score_patent, score_agent, score_inventor, score_ipc, score_applicant):
        result = {}
        # 查询各种实体
        result['专利'] = self.search_entities('专利', score_patent)
        result['代理机构'] = self.search_entities('代理机构', score_agent)
        result['发明人'] = self.search_entities('发明人', score_inventor)
        result['IPC'] = self.search_entities('IPC', score_ipc)
        result['申请人'] = self.search_entities('申请人', score_applicant)

        # 查询各种关系
        result['专利与专利'] = self.search_relationships('专利与专利', score_patent, score_patent)
        result['专利与申请人'] = self.search_relationships('专利与申请人', score_patent, score_applicant)
        result['专利与IPC'] = self.search_relationships('专利与IPC', score_patent, score_ipc)
        result['专利与发明人'] = self.search_relationships('专利与发明人', score_patent, score_inventor)
        result['专利与代理机构'] = self.search_relationships('专利与代理机构', score_patent, score_agent)

        return {
            "status": "success",
            "message": "数据查询成功",
            "results": result
        }

    '''查找专利地理位置信息'''
    '''功能:根据专利的申请人位置，确定专利的位置，并筛选出时间小于时间的专利数量'''
    '''
    参数:
        "time"="值"
    返回:
        查询结果的数组
    '''

    def location_patent_search(self, time):
        # 转换时间格式
        formatted_time = datetime.strptime(time, '%Y.%m.%d').strftime('%Y-%m-%d')

        # 初始化省份列表
        provinces = [
            '北京', '天津', '上海', '重庆', '河北', '河南', '云南', '辽宁', '黑龙江',
            '湖南', '安徽', '山东', '新疆', '江苏', '浙江', '江西', '湖北', '广西', '甘肃',
            '山西', '内蒙古', '陕西', '吉林', '福建', '贵州', '广东', '青海', '西藏', '四川',
            '宁夏', '海南', '台湾', '香港', '澳门'
        ]

        # 定义结果模板
        patent_counts = [{'name': province, 'value': 0} for province in provinces]
        patent_scores = [{'name': province, 'value': 0} for province in provinces]
        result_template = {
            '专利数量': patent_counts,
            '专利重要度': patent_scores
        }

        # 定义查询语句
        query = """
        MATCH (p:Patent)-[:APPLIED_BY]->(a:Applicant)
        WHERE p.公开日 <= $time
        RETURN a.省份 as Province, COUNT(p) as PatentCount, SUM(p.pageRankScore) as TotalPageRankScore
        """
        # 执行查询
        results = self.graph.run(query, time=formatted_time).data()

        # 更新结果
        for result in results:
            if result['Province']:
                for entry in result_template['专利数量']:
                    if entry['name'] == result['Province']:
                        entry['value'] += result['PatentCount']
                for entry in result_template['专利重要度']:
                    if entry['name'] == result['Province']:
                        entry['value'] += result['TotalPageRankScore']

        return result_template

    # 省份IPC占比
    def location_IPC_search(self, time):
        # 转换日期格式以匹配数据库中的格式
        formatted_time = datetime.strptime(time, '%Y-%m-%d').strftime('%Y.%m.%d')

        # 查询语句
        query = """
        MATCH (p:Patent)-[:APPLIED_BY]->(a:Applicant), (p)-[:BELONGS_TO]->(ipc:IPC)
        WHERE p.公开日 <= $formatted_time
        RETURN a.省份 AS Province, ipc.名称 AS IPCName, COUNT(p) AS Count
        ORDER BY a.省份, COUNT(p) DESC
        """

        # 执行查询
        results = self.graph.run(query, formatted_time=formatted_time).data()

        # 组织数据
        province_ipc_data = {}
        provinces = [
            '北京', '天津', '上海', '重庆', '河北', '河南', '云南', '辽宁', '黑龙江',
            '湖南', '安徽', '山东', '新疆', '江苏', '浙江', '江西', '湖北', '广西', '甘肃',
            '山西', '内蒙古', '陕西', '吉林', '福建', '贵州', '广东', '青海', '西藏', '四川',
            '宁夏', '海南', '台湾', '香港', '澳门'
        ]
        # 初始化字典
        for province in provinces:
            province_ipc_data[province] = []

        # 填充数据
        for result in results:
            province = result['Province']
            if result['Count'] >= 10:  # 只添加Count大于或等于5的数据
                if province in province_ipc_data:
                    province_ipc_data[province].append({
                        'name': result['IPCName'],
                        'value': result['Count']
                    })

        return province_ipc_data

    # 省份patent占比
    def location_patent_importance_search(self, time):
        # 转换日期格式以匹配数据库中的格式
        formatted_time = datetime.strptime(time, '%Y-%m-%d').strftime('%Y.%m.%d')

        # 查询语句，列出每个省份的符合条件的专利和它们的pageRankScore
        query = """
         MATCH (p:Patent)-[:APPLIED_BY]->(a:Applicant)
         WHERE p.公开日 <= $formatted_time AND p.pageRankScore > 7 AND a.省份 IS NOT NULL
         RETURN a.省份 AS Province, p.名称 AS PatentName, p.pageRankScore AS PageRankScore
         ORDER BY a.省份, p.pageRankScore DESC
         """

        # 执行查询
        results = self.graph.run(query, formatted_time=formatted_time).data()

        # 组织数据
        province_patent_data = {}
        provinces = [
            '北京', '天津', '上海', '重庆', '河北', '河南', '云南', '辽宁', '黑龙江',
            '湖南', '安徽', '山东', '新疆', '江苏', '浙江', '江西', '湖北', '广西', '甘肃',
            '山西', '内蒙古', '陕西', '吉林', '福建', '贵州', '广东', '青海', '西藏', '四川',
            '宁夏', '海南', '台湾', '香港', '澳门'
        ]
        # 初始化字典
        for province in provinces:
            province_patent_data[province] = []

        # 填充数据
        for result in results:
            province = result['Province']
            if province and province in province_patent_data:
                province_patent_data[province].append({
                    'name': result['PatentName'],
                    'value': result['PageRankScore']
                })

        return province_patent_data

    # applicant省份占比
    def location_applicant_importance_search(self, time):
        # 转换日期格式以匹配数据库中的格式
        formatted_time = datetime.strptime(time, '%Y-%m-%d').strftime('%Y.%m.%d')

        # 查询语句，聚合每个省份申请人的pageRankScore
        query = """
           MATCH (p:Patent)-[:APPLIED_BY]->(a:Applicant)
           WHERE p.公开日 <= $formatted_time AND a.省份 IS NOT NULL
           RETURN a.省份 AS Province, a.名称 AS ApplicantName, SUM(p.pageRankScore) AS TotalImportance
           ORDER BY a.省份, SUM(p.pageRankScore) DESC
           """

        # 执行查询
        results = self.graph.run(query, formatted_time=formatted_time).data()

        # 组织数据
        province_applicant_data = {}
        provinces = [
            '北京', '天津', '上海', '重庆', '河北', '河南', '云南', '辽宁', '黑龙江',
            '湖南', '安徽', '山东', '新疆', '江苏', '浙江', '江西', '湖北', '广西', '甘肃',
            '山西', '内蒙古', '陕西', '吉林', '福建', '贵州', '广东', '青海', '西藏', '四川',
            '宁夏', '海南', '台湾', '香港', '澳门'
        ]
        # 初始化字典
        for province in provinces:
            province_applicant_data[province] = []

        # 填充数据
        for result in results:
            province = result['Province']
            if result['TotalImportance'] >= 25:
                if province and province in province_applicant_data:
                    province_applicant_data[province].append({
                        'name': result['ApplicantName'],
                        'value': result['TotalImportance']
                    })

        return province_applicant_data

    # inventor省份占比
    # 查询某个时间结点，对申请人专利pageRankScore的统计和
    # 思路：先遍历出所有的专利，筛选出时间结点在"2024.01.01"之前的专利，再通过关系

    def location_inventor_importance_search(self, time):
        # 转换日期格式以匹配数据库中的格式
        formatted_time = datetime.strptime(time, '%Y-%m-%d').strftime('%Y.%m.%d')

        # 查询语句，聚合每个省份发明人的pageRankScore
        query = """
        MATCH (p:Patent)-[:APPLIED_BY]->(a:Applicant), (p)-[:INVENTED_BY]->(i:Inventor)
        WHERE p.公开日 <= $formatted_time AND a.省份 IS NOT NULL
        RETURN a.省份 AS Province, i.名称 AS InventorName, SUM(p.pageRankScore) AS TotalImportance
        ORDER BY a.省份, SUM(p.pageRankScore) DESC
        """

        # 执行查询
        results = self.graph.run(query, formatted_time=formatted_time).data()

        # 组织数据
        province_inventor_data = {}
        provinces = [
            '北京', '天津', '上海', '重庆', '河北', '河南', '云南', '辽宁', '黑龙江',
            '湖南', '安徽', '山东', '新疆', '江苏', '浙江', '江西', '湖北', '广西', '甘肃',
            '山西', '内蒙古', '陕西', '吉林', '福建', '贵州', '广东', '青海', '西藏', '四川',
            '宁夏', '海南', '台湾', '香港', '澳门'
        ]
        # 初始化字典
        for province in provinces:
            province_inventor_data[province] = []

        # 填充数据
        for result in results:
            province = result['Province']
            if result['TotalImportance'] >= 25:
                if province and province in province_inventor_data:
                    province_inventor_data[province].append({
                        'name': result['InventorName'],
                        'value': result['TotalImportance']
                    })

        return province_inventor_data

        """
        功能: 根据专利公开号查询与该专利相关的所有实体结点和关系
        参数:
            publication_number: 专利的公开号
        返回:
            成功: 返回相关实体和关系的详细信息
            失败: 返回错误信息
        """

    def find_patent_details(self, publication_number):
        try:
            # 初始化结果字典
            results = {
                "专利": [],
                "代理机构": [],
                "发明人": [],
                "IPC": [],
                "申请人": [],
                "专利与专利": [],
                "专利与申请人": [],
                "专利与IPC": [],
                "专利与发明人": [],
                "专利与代理机构": []
            }

            # 执行专利本身的查询
            patent_query = f"{self.search_match['专利']} WHERE n.公开号 = '{publication_number}' {self.search_return['专利']}"
            patent_result = self.graph.run(patent_query).data()
            results['专利'] = [{'id': n['id(n)'], 'type': '专利', **dict(n['n'])} for n in patent_result]

            # 列表，用于保存所有要执行的查询
            queries = [
                (
                    f"{self.search_match['代理机构']}<-[:REPRESENTED_BY]-(p:Patent) WHERE p.公开号 = '{publication_number}' {self.search_return['代理机构']}",
                    "代理机构"),
                (
                    f"{self.search_match['发明人']}<-[:INVENTED_BY]-(p:Patent) WHERE p.公开号 = '{publication_number}' {self.search_return['发明人']}",
                    "发明人"),
                (
                    f"{self.search_match['IPC']}<-[:BELONGS_TO]-(p:Patent) WHERE p.公开号 = '{publication_number}' {self.search_return['IPC']}",
                    "IPC"),
                (
                    f"{self.search_match['申请人']}<-[:APPLIED_BY]-(p:Patent) WHERE p.公开号 = '{publication_number}' {self.search_return['申请人']}",
                    "申请人"),
                (
                    f"{self.search_match['专利与专利']} WHERE n.公开号 = '{publication_number}' {self.search_return['专利与专利']}",
                    "专利与专利"),
                (
                    f"{self.search_match['专利与申请人']} WHERE n.公开号 = '{publication_number}' {self.search_return['专利与申请人']}",
                    "专利与申请人"),
                (
                    f"{self.search_match['专利与IPC']} WHERE n.公开号 = '{publication_number}' {self.search_return['专利与IPC']}",
                    "专利与IPC"),
                (
                    f"{self.search_match['专利与发明人']} WHERE n.公开号 = '{publication_number}' {self.search_return['专利与发明人']}",
                    "专利与发明人"),
                (
                    f"{self.search_match['专利与代理机构']} WHERE n.公开号 = '{publication_number}' {self.search_return['专利与代理机构']}",
                    "专利与代理机构")
            ]

            # 对每个查询进行处理
            for query, key in queries:
                query_result = self.graph.run(query).data()
                if key.startswith("专利与"):  # 处理关系数据
                    results[key] = [
                        {"from": r['from'], "to": r['to'], "id_from": r['id_from'], "id_to": r['id_to'],
                         "rel": r['rel'], "from_type": "专利", "to_type": key.split('与')[1]}
                        for r in query_result
                    ]
                else:  # 处理实体数据
                    results[key].extend([{'id': n['id(n)'], 'type': key, **dict(n['n'])} for n in query_result])

            return {"status": "success", "message": "数据查询成功", "results": results}
        except Exception as e:
            print(f"查询失败: {e}")
            return {"status": "error", "message": str(e)}

    # 统计专利的被引次数
    def count_citations(self, publication_number, csv_file_path):
        try:
            citation_count = 0
            if not os.path.exists(csv_file_path):
                raise FileNotFoundError(f"CSV file not found: {csv_file_path}")

            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader)  # 跳过表头
                for row in reader:
                    if row[0] == publication_number:
                        citation_count += 1
            return {"status": "success", "publication_number": publication_number, "citation_count": citation_count}
        except Exception as e:
            print(f"统计被引次数失败: {e}")
            return {"status": "error", "message": str(e)}

    # 统计同类型专利数量
    def count_exact_ipc_related_patents(self, publication_number):
        try:
            # 查询指定专利的所有IPC分类号
            ipc_query = """
                MATCH (p:Patent {公开号: $publication_number})-[:BELONGS_TO]->(ipc:IPC)
                RETURN COLLECT(ipc.名称) as IPCNames
                """
            ipc_results = self.graph.run(ipc_query, publication_number=publication_number).data()

            if not ipc_results:
                return {"status": "error", "message": "No IPCs found for the given patent"}

            ipc_names = ipc_results[0]['IPCNames']
            ipc_names_set = set(ipc_names)

            # 查询所有与指定专利有完全相同IPC分类号的专利数量
            count_query = """
                MATCH (p:Patent)-[:BELONGS_TO]->(ipc:IPC)
                WHERE ALL(ipc_name IN $ipc_names WHERE (p)-[:BELONGS_TO]->(:IPC {名称: ipc_name}))
                WITH p, COLLECT(ipc.名称) as ipcNames
                WHERE SIZE(ipcNames) = SIZE($ipc_names)
                RETURN COUNT(DISTINCT p) as RelatedPatentCount
                """
            count_result = self.graph.run(count_query, ipc_names=ipc_names).data()

            if count_result:
                return {"status": "success", "related_patent_count": count_result[0]['RelatedPatentCount']}
            else:
                return {"status": "success", "related_patent_count": 0}
        except Exception as e:
            print(f"查询失败: {e}")
            return {"status": "error", "message": str(e)}

    # 查询专利的时间价值
    def calculate_time_value(self, publication_number):
        try:
            # 查询专利的申请日和公开日
            query = """
            MATCH (p:Patent {公开号: $publication_number})
            RETURN p.申请日 as ApplicationDate, p.公开日 as PublicationDate
            """
            result = self.graph.run(query, publication_number=publication_number).data()

            if not result:
                return {"status": "error", "message": "No patent found with the given publication number"}

            application_date = datetime.strptime(result[0]['ApplicationDate'], '%Y.%m.%d')
            publication_date = datetime.strptime(result[0]['PublicationDate'], '%Y.%m.%d')

            # 计算专利生命周期
            lifecycle_days = (publication_date - application_date).days

            # 假设时间价值分数为生命周期的天数
            time_value_score = lifecycle_days

            return {"status": "success", "time_value_score": time_value_score}
        except Exception as e:
            print(f"查询失败: {e}")
            return {"status": "error", "message": str(e)}

    # 获取专利的图影响力
    def get_page_rank_score(self, publication_number):
        try:
            query = """
            MATCH (p:Patent {公开号: $publication_number})
            RETURN p.pageRankScore as PageRankScore
            """
            result = self.graph.run(query, publication_number=publication_number).data()

            if not result:
                return {"status": "error", "message": "No patent found with the given publication number"}

            page_rank_score = result[0]['PageRankScore']
            return {"status": "success", "page_rank_score": page_rank_score}
        except Exception as e:
            print(f"查询失败: {e}")
            return {"status": "error", "message": str(e)}

    # 模拟生成专利的法律状态
    def simulate_legal_status(self, publication_number):
        try:
            # 假设所有专利的法律状态都为有效
            legal_status = "有效"
            return {"status": "success", "legal_status": legal_status}
        except Exception as e:
            print(f"模拟法律状态失败: {e}")
            return {"status": "error", "message": str(e)}

    # 获取专利详细信息，包括所有查询函数
    def get_patent_details(self, publication_number, csv_file_path):
        try:
            # 被引次数
            citation_result = self.count_citations(publication_number, csv_file_path)

            # 同类型专利数量
            ipc_related_result = self.count_exact_ipc_related_patents(publication_number)

            # 时间价值
            time_value_result = self.calculate_time_value(publication_number)

            # 图影响力
            page_rank_result = self.get_page_rank_score(publication_number)

            # 法律状态
            legal_status_result = self.simulate_legal_status(publication_number)

            return {
                "status": "success",
                "publication_number": publication_number,
                "citation_count": citation_result.get("citation_count", 0),
                "related_patent_count": ipc_related_result.get("related_patent_count", 0),
                "time_value_score": time_value_result.get("time_value_score", 0),
                "page_rank_score": page_rank_result.get("page_rank_score", 0),
                "legal_status": legal_status_result.get("legal_status", "未知")
            }
        except Exception as e:
            print(f"查询失败: {e}")
            return {"status": "error", "message": str(e)}

    # 根据类型和名称查询相关专利的信息
    def search_related_patents(self, entity_type, name):
        if entity_type not in self.search_label:
            return {"status": "error", "message": "Invalid entity type"}

        # 构建查询语句
        query = f"""
            MATCH (e:{self.search_label[entity_type]} {{名称: $name}})<-[:{self.get_relation_type(entity_type)}]-(p:Patent)
            RETURN p.名称 as 专利名称, substring(p.公开日, 0, 4) as 专利年份, p.pageRankScore as 专利重要度
            ORDER BY 专利年份
            """

        try:
            result = self.graph.run(query, name=name).data()
            return {"status": "success", "data": result}
        except Exception as e:
            print(f"查询失败: {e}")
            return {"status": "error", "message": str(e)}

    def get_relation_type(self, entity_type):
        if entity_type == '代理机构':
            return 'REPRESENTED_BY'
        elif entity_type == '发明人':
            return 'INVENTED_BY'
        elif entity_type == 'IPC':
            return 'BELONGS_TO'
        elif entity_type == '申请人':
            return 'APPLIED_BY'
        return None

    def find_patent_community_details(self, publication_number):
        try:
            # 获取专利所属的社群ID
            community_query = f"MATCH (p:Patent {{公开号: '{publication_number}'}}) RETURN p.communityId AS communityId"
            community_id = self.graph.run(community_query).evaluate()
            if not community_id:
                return {"status": "error", "message": "No community ID found for the given publication number"}

            # 初始化结果字典
            results = {
                "IPC": [],
                "专利": [],
                "专利与IPC": [],
                "专利与专利": [],
                "专利与代理机构": [],
                "专利与发明人": [],
                "专利与申请人": [],
                "代理机构": [],
                "发明人": [],
                "申请人": []
            }

            # 列表，用于保存所有要执行的查询
            queries = [
                (
                    f"{self.search_match['专利']} WHERE n.communityId = {community_id} {self.search_return['专利']}",
                    "专利"
                ),
                (
                    f"{self.search_match['代理机构']} WHERE n.communityId = {community_id} {self.search_return['代理机构']}",
                    "代理机构"
                ),
                (
                    f"{self.search_match['发明人']} WHERE n.communityId = {community_id} {self.search_return['发明人']}",
                    "发明人"
                ),
                (
                    f"{self.search_match['IPC']} WHERE n.communityId = {community_id} {self.search_return['IPC']}",
                    "IPC"
                ),
                (
                    f"{self.search_match['申请人']} WHERE n.communityId = {community_id} {self.search_return['申请人']}",
                    "申请人"
                ),
                # 关系查询需要特别处理
                (
                    f"{self.search_match['专利与专利']} WHERE n.communityId = {community_id} AND m.communityId = {community_id} {self.search_return['专利与专利']}",
                    "专利与专利"
                ),
                (
                    f"{self.search_match['专利与IPC']} WHERE n.communityId = {community_id} AND m.communityId = {community_id} {self.search_return['专利与专利']}",
                    "专利与IPC"
                ),
                (
                    f"{self.search_match['专利与申请人']} WHERE n.communityId = {community_id} AND m.communityId = {community_id} {self.search_return['专利与专利']}",
                    "专利与申请人"
                ),
                (
                    f"{self.search_match['专利与代理机构']} WHERE n.communityId = {community_id} AND m.communityId = {community_id} {self.search_return['专利与专利']}",
                    "专利与代理机构"
                ),
                (
                    f"{self.search_match['专利与发明人']} WHERE n.communityId = {community_id} AND m.communityId = {community_id} {self.search_return['专利与专利']}",
                    "专利与发明人"
                ),
            ]

            # 对每个查询进行处理
            for query, key in queries:
                query_result = self.graph.run(query).data()
                for item in query_result:
                    if key.startswith("专利与"):  # 处理关系数据
                        results[key].append({
                            "from": item['from'],
                            "to": item['to'],
                            "id_from": item['id_from'],
                            "id_to": item['id_to'],
                            "rel": item['rel'],
                            "from_type": "专利",
                            "to_type": key.split('与')[1]
                        })
                    else:  # 处理实体数据
                        node_data = {'id': item['id(n)'], 'type': key, **dict(item['n'])}
                        results[key].append(node_data)

            return {"status": "success", "message": "Data retrieval successful", "results": results}
        except Exception as e:
            return {"status": "error", "message": f"Query failed: {str(e)}"}

    def find_shortest_paths(self, start_name, end_name, start_label, end_label):
        try:
            query = f"""
                MATCH (start:{start_label} {{名称: '{start_name}'}}), (end:{end_label} {{名称: '{end_name}'}}),
                      path = allShortestPaths((start)-[*]-(end))
                UNWIND nodes(path) as n
                UNWIND relationships(path) as r
                WITH n, r
                ORDER BY id(n)
                WITH COLLECT(DISTINCT n) as nodes, COLLECT(DISTINCT r) as rels
                RETURN 
                    [node IN nodes WHERE 'Patent' IN labels(node)] as patentNodes,
                    [node IN nodes WHERE 'Agent' IN labels(node)] as agentNodes,
                    [node IN nodes WHERE 'Inventor' IN labels(node)] as inventorNodes,
                    [node IN nodes WHERE 'IPC' IN labels(node)] as ipcNodes,
                    [node IN nodes WHERE 'Applicant' IN labels(node)] as applicantNodes,
                    [rel IN rels WHERE type(rel) = 'CITES_BY'] as patentRelations,
                    [rel IN rels WHERE type(rel) = 'APPLIED_BY'] as applicantRelations,
                    [rel IN rels WHERE type(rel) = 'BELONGS_TO'] as ipcRelations,
                    [rel IN rels WHERE type(rel) = 'INVENTED_BY'] as inventorRelations,
                    [rel IN rels WHERE type(rel) = 'REPRESENTED_BY'] as agentRelations
            """
            result = self.graph.run(query).data()
            if not result:
                return {"status": "error", "message": "No paths found"}

            formatted_result = {
                "专利": [self.format_node(node) for node in result[0]['patentNodes']],
                "代理机构": [self.format_node(node) for node in result[0]['agentNodes']],
                "发明人": [self.format_node(node) for node in result[0]['inventorNodes']],
                "IPC": [self.format_node(node) for node in result[0]['ipcNodes']],
                "申请人": [self.format_node(node) for node in result[0]['applicantNodes']],
                "专利与专利": [self.format_relation(rel) for rel in result[0]['patentRelations']],
                "专利与申请人": [self.format_relation(rel) for rel in result[0]['applicantRelations']],
                "专利与IPC": [self.format_relation(rel) for rel in result[0]['ipcRelations']],
                "专利与发明人": [self.format_relation(rel) for rel in result[0]['inventorRelations']],
                "专利与代理机构": [self.format_relation(rel) for rel in result[0]['agentRelations']]
            }

            return {
                "status": "success",
                "message": "Data retrieval successful",
                "results": formatted_result
            }
        except Exception as e:
            return {"status": "error", "message": f"Query failed: {str(e)}"}

    def format_node(self, node):
        # 确保node.labels是可迭代并获取第一个标签作为类型，如果没有标签，则默认为None
        node_type = next(iter(node.labels), None)

        # 映射字典
        label_mapping = {
            'Patent': '专利',
            'Agent': '代理机构',
            'Inventor': '发明人',
            'IPC': 'IPC',
            'Applicant': '申请人'
        }

        # 使用映射字典进行转换
        node_type_translated = label_mapping.get(node_type, node_type)

        return {
            'id': node.identity,
            'type': node_type_translated,
            'communityId': node.get('communityId'),
            'pageRankScore': node.get('pageRankScore'),
            '公开号': node.get('公开号'),
            '公开日': node.get('公开日'),
            '名称': node.get('名称'),
            '摘要': node.get('摘要'),
            '文献类型': node.get('文献类型'),
            '申请号': node.get('申请号'),
            '申请日': node.get('申请日')
        }

    def format_relation(self, rel):
        # 从关系对象中提取起始和结束结点，获取相关属性
        start_node = rel.start_node
        end_node = rel.end_node
        start_node_type = next(iter(start_node.labels), None)
        end_node_type = next(iter(end_node.labels), None)

        # 使用 type() 函数获取关系的类型字符串
        relation_type = type(rel).__name__

        return {
            'from': start_node.get('公开号', ''),
            'to': end_node.get('名称', ''),
            'id_from': str(start_node.identity),
            'id_to': str(end_node.identity),
            'rel': relation_type,
            'from_type': start_node_type,
            'to_type': end_node_type
        }


if __name__ == '__main__':
    url = 'http://localhost:7474/browser/'
    user = 'neo4j'
    password = 'CHW123d456'
    query_instance = Neo4jQuery(url, user, password)
    # 测试1
    # print(query_instance.search_entities(label="Inventor", property_value="何川"))

    # 调用get_filtered_data函数进行测试
    # 示例参数：查询专利、代理机构、发明人、IPC、申请人，返回数量为10，时间范围从1970.01.01到2025.01.01
    # test_results = query_instance.get_filtered_data(True, True, True, True, True, 10, '1970.01.01', '2025.01.01')
    #
    # # 打印测试结果
    # print("测试结果：")
    # for result in test_results:
    #     print(result)
    # test_results = query_instance.test_complex_entities_and_relationships()
    # 查询特定日期之前的专利地理位置信息
    # result = query_instance.location_inventor_importance_search('2024-01-01')
    # 查询指定专利的被引次数
    # 价值维度
    # publication_number = 'CN101225743A'
    # citation_result = query_instance.count_citations('CN101225743A', 'data/index/关系-专利和专利-处理前.csv')
    # result = query_instance.count_exact_ipc_related_patents('CN101225743A')
    # print(result)
    # print(citation_result)
    # result = query_instance.calculate_time_value(publication_number)
    # print(result)

    entity_type = '发明人'
    name = '何川'
    result = query_instance.search_related_patents(entity_type, name)
    print(result)
