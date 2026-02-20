from flask import Flask, request, jsonify
from flask.views import MethodView
from flask_cors import CORS
from neo4j.export_data import Neo4jQuery  # 确保导入正确
from datetime import datetime
# 创建 Elasticsearch 索引类的实例
from mysql_to_elasticsearch import ESCreateIndex

app = Flask(__name__)
CORS(app)  # 简化跨域处理初始化

# 数据库的基础配置
url = 'http://localhost:7474/browser/'
user = 'neo4j'
password = 'CHW123d456'

es = ESCreateIndex("patent")


# 首页请求处理
@app.route('/')
def hello_world():
    return 'Hello World!'


# 宏观展示界面的查询接口
# app.py
@app.route('/datas', methods=['GET'])
def get_data():
    try:
        # 从请求参数中获取分数阈值
        score_patent = float(request.args.get('score_patent', 0))
        score_agent = float(request.args.get('score_agent', 0))
        score_inventor = float(request.args.get('score_inventor', 0))
        score_ipc = float(request.args.get('score_ipc', 0))
        score_applicant = float(request.args.get('score_applicant', 0))

        # 创建 Neo4jQuery 实例
        query_instance = Neo4jQuery(url, user, password)

        # 调用 get_filtered_data 方法获取数据
        data = query_instance.get_filtered_data(score_patent, score_agent, score_inventor, score_ipc, score_applicant)

        # 返回 JSON 格式的查询结果
        return jsonify(data)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })


# 获取专利地理信息的接口
@app.route('/datas/location', methods=['GET'])
def location_data():
    time = request.args.get('time')
    if not time:
        return jsonify({
            "message": "时间参数缺失",
            "status": "error"
        }), 400

    try:
        # 首先尝试 YYYY-MM-DD 格式
        parsed_time = datetime.strptime(time, '%Y-%m-%d')
    except ValueError:
        return jsonify({
            "message": f"时间格式错误，无法解析: {time}",
            "status": "error"
        }), 400

    # 将日期转换为 YYYY.MM.DD 格式
    formatted_time = parsed_time.strftime('%Y.%m.%d')

    # 创建Neo4jQuery实例
    # 确保 Neo4jQuery 和其方法 location_patent_search 已定义并可用
    query_instance = Neo4jQuery('bolt://localhost:7687', user, password)

    try:
        results = query_instance.location_patent_search(formatted_time)
        return jsonify({
            "message": "数据查询成功",
            "results": results,
            "status": "success"
        }), 200
    except Exception as e:
        return jsonify({
            "message": f"查询过程中发生错误: {str(e)}",
            "status": "error"
        }), 500


# 新的地理位置综合查询接口
@app.route('/datas/location_summary', methods=['GET'])
def location_data_summary():
    time = request.args.get('time')
    if not time:
        return jsonify({
            "message": "时间参数缺失",
            "status": "error"
        }), 400

    try:
        # 格式化时间
        parsed_time = datetime.strptime(time, '%Y-%m-%d').date()  # 确保时间是正确的格式
    except ValueError:
        return jsonify({
            "message": f"时间格式错误，无法解析: {time}",
            "status": "error"
        }), 400

    # 创建Neo4jQuery实例
    query_instance = Neo4jQuery('bolt://localhost:7687', user, password)

    try:
        ipc_results = query_instance.location_IPC_search(time)  # 使用原始时间字符串
        patent_results = query_instance.location_patent_importance_search(time)
        inventor_results = query_instance.location_inventor_importance_search(time)
        applicant_results = query_instance.location_applicant_importance_search(time)

        # 组织所有结果
        all_results = {
            "ipc": ipc_results,
            "patent": patent_results,
            "inventor": inventor_results,
            "applicant": applicant_results
        }

        return jsonify({
            "status": "success",
            "message": "数据查询成功",
            "results": all_results
        }), 200
    except Exception as e:
        return jsonify({
            "message": f"查询过程中发生错误: {str(e)}",
            "status": "error"
        }), 500


# 添加专利搜索的接口
@app.route('/search/patent', methods=['GET'])
def search_patent():
    query = request.args.get('query', default='', type=str)
    page = request.args.get('page', default=1, type=int)
    page_size = request.args.get('page_size', default=10, type=int)

    # 调用搜索方法，现在包括总结果数
    results, search_time, total_results = es.search_patent_name(query, page, page_size)

    # 返回包括结果、搜索耗时和总结果数的JSON
    return jsonify({
        "results": results,
        "took": search_time,
        "total": total_results
    })


@app.route('/search/patent_details', methods=['GET'])
def get_patent_details():
    """
    查询与给定专利公开号相关的所有实体和关系。
    """
    publication_number = request.args.get('publication_number')  # 从请求中获取专利公开号
    if not publication_number:
        return jsonify({"status": "error", "message": "No publication number provided"}), 400

    # 使用专利公开号调用查询方法
    try:
        query_instance = Neo4jQuery('bolt://localhost:7687', user, password)
        results = query_instance.find_patent_details(publication_number)
        return jsonify(results)  # 返回查询结果
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# 查询专利详细信息的接口
@app.route('/patent_info', methods=['GET'])
def get_patent_info():
    try:
        publication_number = request.args.get('publication_number')
        if not publication_number:
            return jsonify({"status": "error", "message": "No publication number provided"})

        # 创建 Neo4jQuery 实例
        query_instance = Neo4jQuery(url, user, password)
        csv_file_path = 'neo4j/data/index/关系-专利和专利-处理前.csv'
        # 获取专利详细信息
        details = query_instance.get_patent_details(publication_number, csv_file_path)

        # 返回 JSON 格式的查询结果
        return jsonify(details)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })


# 添加新的查询接口
# http://127.0.3.1:5001/search/related_patents?entity_type=申请人&name=山东大学
@app.route('/search/related_patents', methods=['GET'])
def search_related_patents():
    entity_type = request.args.get('entity_type')
    name = request.args.get('name')

    if not entity_type or not name:
        return jsonify({"status": "error", "message": "Entity type and name are required"}), 400

    # 创建 Neo4jQuery 实例
    query_instance = Neo4jQuery(url, user, password)

    # 调用 search_related_patents 方法获取数据
    try:
        data = query_instance.search_related_patents(entity_type, name)
        return jsonify(data)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# 查询社群图
@app.route('/search/community_patent_details', methods=['GET'])
def get_community_patent_details():
    """
    查询与给定专利公开号相同社群的所有实体和关系。
    """
    publication_number = request.args.get('publication_number')  # 从请求中获取专利公开号
    if not publication_number:
        return jsonify({"status": "error", "message": "No publication number provided"}), 400

    # 使用专利公开号调用查询社群的方法
    try:
        query_instance = Neo4jQuery('bolt://localhost:7687', user, password)
        results = query_instance.find_patent_community_details(publication_number)
        return jsonify(results)  # 返回查询结果
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/search/shortest_paths', methods=['GET'])
def get_shortest_paths():
    """
    根据提供的起始和终止节点名称查询所有最短路径上的节点和关系。
    """
    start_name = request.args.get('start_name')  # 起始节点名称
    end_name = request.args.get('end_name')  # 终止节点名称
    start_label = request.args.get('start_label')  # 起始节点的标签类型
    end_label = request.args.get('end_label')  # 终止节点的标签类型

    if not start_name or not end_name or not start_label or not end_label:
        return jsonify({"status": "error", "message": "Missing required parameters"}), 400

    # 使用节点名称和标签调用查询最短路径的方法
    try:
        query_instance = Neo4jQuery('bolt://localhost:7687', user, password)  # 更新为你的实际用户名和密码
        results = query_instance.find_shortest_paths(start_name, end_name, start_label, end_label)
        return jsonify(results)  # 返回查询结果
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# 响应第一个请求前先创建图投影
@app.before_first_request
def create_graph_projection():
    query_instance = Neo4jQuery(url, user, password)
    create_projection_query = """
    CALL gds.graph.project(
      'fullGraph',
      ['Patent', 'Agent', 'Inventor', 'IPC', 'Applicant'],  
      {
        CITES_BY: { type: 'CITES_BY', orientation: 'NATURAL' },  //NATURAL表示保持原有方向
        APPLIED_BY: { type: 'APPLIED_BY', orientation: 'UNDIRECTED' },
        BELONGS_TO: { type: 'BELONGS_TO', orientation: 'UNDIRECTED' },
        INVENTED_BY: { type: 'INVENTED_BY', orientation: 'UNDIRECTED' },
        REPRESENTED_BY: { type: 'REPRESENTED_BY', orientation: 'UNDIRECTED' }
      }
    )
    """
    query_instance.graph.run(create_projection_query)
    pagerank_query = """
    CALL gds.pageRank.write(
      'fullGraph',
      {
        writeProperty: 'pageRankScore',
        dampingFactor: 0.85,
        maxIterations: 20
      }
    )
    YIELD nodePropertiesWritten, ranIterations, didConverge
    RETURN nodePropertiesWritten, ranIterations, didConverge
    """
    results = query_instance.graph.run(pagerank_query)
    print(results)  # 打印 PageRank 计算结果，用于调试


# 结束程序后删除图投影
import atexit


def drop_graph_projection():
    query_instance = Neo4jQuery(url, user, password)
    drop_projection_query = "CALL gds.graph.drop('fullGraph')"
    query_instance.graph.run(drop_projection_query)


atexit.register(drop_graph_projection)

if __name__ == '__main__':
    app.run()
