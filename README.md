# 基于 Neo4j 的产业链知识图谱毕设项目

本仓库用于存放毕业设计相关代码与数据处理脚本，核心是 **Django + Neo4j** 的知识图谱系统，并包含独立的前端可视化项目与数据清洗脚本。

## 项目展示

![系统封面](image/cover.png)

### 系统架构

![系统总体功能架构](image/系统总体功能架构.png)
![系统总体技术架构](image/系统总体技术架构.png)
![知识图谱设计](image/知识图谱设计.png)
![图谱关系说明](image/图谱关系说明.png)
![专利图谱实体和关系数量统计](image/专利图谱实体和关系数量统计.png)

### 界面与功能效果

![专利知识图谱展示](image/专利知识图谱展示.png)
![专利全景展示模块](image/专利全景展示模块.png)
![专利详情界面](image/专利详情界面.png)
![专利关系检索](image/专利关系检索.png)
![专利社群图](image/专利社群图.png)

## 项目结构

- `longma-neo4j`：后端主项目（Django），负责知识图谱查询、页面渲染与用户模块。
- `前端/307/kg`：独立前端项目（Vue3 + ECharts + D3），用于图谱可视化展示。
- `数据/数据集处理`：数据集处理与图谱入库脚本（Python）。
- `前端/vben/vue-vben-admin`：第三方前端模板（可选，不是本项目核心业务代码）。

## 技术栈

- 后端：Django 3.2、py2neo、SQLite（开发态）
- 图数据库：Neo4j
- 前端：Vue3、Element Plus、ECharts、D3
- 数据处理：Python + CSV

## 快速开始

### 1) 启动后端（Django）

```bash
cd longma-neo4j
pip install -r requests.txt
python manage.py runserver
```

浏览器访问：`http://127.0.0.1:8000/`

### 2) 启动前端（可选）

```bash
cd 前端/307/kg
npm install
npm run serve
```

### 3) 数据处理脚本（可选）

```bash
cd 数据/数据集处理
python main.py
```

## 上传到 GitHub 的建议

建议上传：

- 项目源码（`longma-neo4j`、`前端/307/kg`、`数据/数据集处理`）
- 轻量级示例数据与说明文档
- 依赖声明文件（如 `requests.txt`、`package.json`）

建议不要上传：

- `node_modules`、日志、缓存、IDE 配置、系统临时文件
- 构建产物（如 `dist`）
- 本地环境文件（如 `.env`）
- 超大原始数据、压缩包备份、临时中间结果

## 注意事项

- 当前代码中存在本地开发配置（如 Django `SECRET_KEY`、Neo4j 连接信息）。若仓库公开，建议改为环境变量管理后再发布。
- 若只想展示毕设成果，建议以 `longma-neo4j + 前端/307/kg + 数据/数据集处理` 作为核心内容，第三方模板目录可不上传。
