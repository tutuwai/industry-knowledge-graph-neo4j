<template>
  <!-- 复选框和标签的容器 -->
  <div class="top-controls">
    <!-- 结点颜色含义与阈值控制 -->
    <!--    专利-->
    <div class="indicator-and-thresholds">
      <div class="node-control">
        <el-tag :style="{ backgroundColor: colors[0], color: 'black' }">
          {{ names[0] }}
        </el-tag>
        <el-input-number v-model="thresholds.patent" :precision="2" :step="0.1"
                         :max="maxValues.patent" :min="minValues.patent" size="small"/>
      </div>
      <!--    代理机构-->
      <div class="node-control">
        <el-tag :style="{ backgroundColor: colors[1], color: 'black' }">
          {{ names[1] }}
        </el-tag>
        <el-input-number v-model="thresholds.agent" :precision="2" :step="0.1"
                         :max="maxValues.agent" :min="minValues.agent" size="small"/>
      </div>
      <!--    发明人-->
      <div class="node-control">
        <el-tag :style="{ backgroundColor: colors[2], color: 'black' }">
          {{ names[2] }}
        </el-tag>
        <el-input-number v-model="thresholds.inventor" :precision="2" :step="0.1"
                         :max="maxValues.inventor" :min="minValues.inventor" size="small"/>
      </div>
      <!--    IPC-->
      <div class="node-control">
        <el-tag :style="{ backgroundColor: colors[3], color: 'black' }">
          {{ names[3] }}
        </el-tag>
        <el-input-number v-model="thresholds.ipc" :precision="2" :step="0.1"
                         :max="maxValues.ipc" :min="minValues.ipc" size="small"/>
      </div>
      <!--    申请人-->
      <div class="node-control">
        <el-tag :style="{ backgroundColor: colors[4], color: 'black' }">
          {{ names[4] }}
        </el-tag>
        <el-input-number v-model="thresholds.applicant" :precision="2" :step="0.1"
                         :max="maxValues.applicant" :min="minValues.applicant" size="small"/>
      </div>
    </div>
  </div>
  <!--图谱可视化区域-->
  <svg>
    <force-graph v-if="displayMode === 'normal'" :url="api1" v-on:clickNode="showNodeInfo" :thresholds="thresholds"
                 @update-statistics="handleStatisticsUpdate"/>

    <ForceGraph_pagerank v-if="displayMode === 'importance'" :url="api1" v-on:clickNode="showNodeInfo"
                         :thresholds="thresholds"
                         @update-statistics="handleStatisticsUpdate"/>
  </svg>
  <!--  统计结点和关系信息-->
  <table class="info">
    <thead>
    <tr>
      <th>分类</th>
      <th>数量</th>
    </tr>
    </thead>
    <tbody>
    <tr v-for="(value, key) in nodeStatistics" :key="key">
      <td>{{ key }}</td>
      <td>{{ value }}</td>
    </tr>
    </tbody>
  </table>
  <!--每个结点的信息-->
  <div class="node_info" v-html="selectedNode ? selectedNodeInfo : ''"></div>
  <!--时间范围输入查询-->
  <div class="in_date">
    <date-picker v-model="dateRange" @update:value="handleDatepickerChange"/>
  </div>
  <!--新增：下拉框选择展示类型-->
  <div class="display_type">
    <el-select v-model="displayMode" placeholder="请选择">
      <el-option label="普通模式" value="normal"></el-option>
      <el-option label="重要度模式" value="importance"></el-option>
    </el-select>
  </div>
  <!--新增：生成图标按钮-->
  <div class="generate_button">
    <el-button type="primary" @click="updateGraph">更新图谱</el-button>
  </div>
</template>
<script>
import DatePicker from "../components/common/DatePicker.vue";
import ForceGraph_pagerank from "../components/GraphPage/ForceGraph_pagerank.vue";
import ForceGraph from "../components/GraphPage/ForceGraph_Graph.vue";
import moment from "moment";

let bool_input = false;
export default {
  name: "HomePage",
  components: {ForceGraph, DatePicker, ForceGraph_pagerank},
  data() {
    return {
      //api1: "http://127.0.3.1:5001/datas?score_patent=5.8&score_agent=6&score_inventor=5&score_ipc=40&score_applicant=5",
      api1: "http://127.0.3.1:5001/search/community_patent_details?publication_number="+ this.$route.params.publicationNumber,
      names: ["专利", '代理机构', '发明人', "IPC", "申请人"],
      colors: ['#6aabd1', '#fdae61', '#e76f51'
        , '#38dac1', '#f53064'],
      search_input: "",
      dateRange: [],
      start_time: "1900-10-10",
      end_time: "2023-4-10",
      selectedNode: null,
      tips_info: null,
      displayMode: "normal",
      nodeStatistics: [],
      publicationNumber: this.$route.params.publicationNumber,  // 从路由获取公开号
      thresholds: {
        patent: 0,
        agent: 0,
        inventor: 0,
        ipc: 0,
        applicant: 0
      },
      maxValues: {
        patent: 17,
        agent: 25,
        inventor: 50,
        ipc: 94,
        applicant: 50
      },
      minValues: {
        patent: 0,
        agent: 0,
        inventor: 0,
        ipc: 0,
        applicant: 0
      },
    };
  },
  methods: {
    //更新结点状态信息
    handleStatisticsUpdate(statistics) {
      this.nodeStatistics = statistics;
      //console.log("ABCDE:", this.nodeStatistics);
    },
    handleInputSubmit(inputString) {
      if (inputString != "") bool_input = true;
      else bool_input = false;
      this.search_input = inputString;
      if (bool_input == true) {
        const params = {
          search_input: this.search_input,
        };
        const queryString = Object.keys(params)
            .map((key) => params[key])
            .join("&");
        this.api1 = "http://127.0.3.1:5050/datas/community?name=" + queryString;
        console.log("new_api1=", this.api1);
      }
    },
    handleDatepickerChange(value) {
      //this.start_time = moment(value[0]).format("YYYY-MM-DD");
      this.end_time = moment(value).format("YYYY-MM-DD");
    },
    // 新增：更新图表方法
    updateGraph() {
      if (bool_input == false) {
        const params = {
          start_time: this.start_time,
          end_time: this.end_time,
        };
        const queryString = Object.keys(params)
            .map((key) => key + "=" + params[key])
            .join("&");
        this.api1 = "http://127.0.3.1:5050/datas?" + queryString;
        console.log("new_api1=", this.api1);
      }
    },
    //展示结点信息
    showNodeInfo(node) {
      if (!node) {
        return;
      }
      this.selectedNode = node;
      //console.log('clicked node:', node);
    },
  },
  computed: {
    selectedNodeInfo() {
      const node = this.selectedNode;
      if (!node) {
        return '';
      }

      // 定义一个对象来映射结点类型
      const nodeTypes = {
        0: '专利',
        1: '代理机构',
        2: '发明人',
        3: 'IPC分类号',
        4: '申请人'
      };

      let info = `<div>结点ID: ${node.id}</div>`;
      info += `<div>结点类型: ${nodeTypes[node.group]}</div>`;  // 添加显示结点类型的行
      // 直接获取结点的 pageRankScore 属性
      info += `<div>结点重要度: ${node.pageRankScore}</div>`; // 显示结点的重要度得分
      switch (node.group) {
        case 0:  // 专利
          info += `
        <div>名称: ${node.名称}</div>
        <div>公开号: ${node.公开号}</div>
        <div>公开日: ${node.公开日}</div>
        <div>摘要: ${node.摘要}</div>
        <div>文献类型: ${node.文献类型}</div>
        <div>申请号: ${node.申请号}</div>
        <div>申请日: ${node.申请日}</div>`;
          break;
        case 1:  // 代理机构
          info += `<div>名称: ${node.名称}</div>`;
          break;
        case 2:  // 发明人
          info += `<div>名称: ${node.名称}</div>`;
          break;
        case 3:  // IPC分类号
          info += `<div>名称: ${node.名称}</div>`;
          break;
        case 4:  // 申请人
          info += `
        <div>名称: ${node.名称}</div>
        <div>邮编: ${node.邮编}</div>`;
          break;
      }
      return info;
    }
    ,
    // 将索引转换为Element UI的标签类型
    getTagType() {
      return (index) => {
        const types = ['primary', 'success', 'info', 'warning', 'danger'];
        return types[index % types.length];  // 循环使用类型，确保不会超出范围
      };
    },
  },
};
</script>

<style lang="less" scoped>
svg {
  width: 1000px;
  height: 510px;
  background-color: #eee;
  margin-left: 20px;
  margin-top: 10px;
}

.top-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  padding: 10px 0;
}

.indicator-and-thresholds {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}

.selectionsselections {
  display: flex; /* 使复选框水平排列 */
  flex-wrap: wrap; /* 允许复选框在必要时换行 */
}

.indicator {
  display: flex;
  align-items: center; /* 垂直居中 */
  gap: 10px; /* 标签之间的间隔 */
}

.node-tag {
  margin-bottom: 0; /* 移除可能的底部外边距 */
  border: none; /* 移除边框 */
}

.node-control {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-left: 20px; /* 增加左边距使标签组向右移动 */
}


.el-input-number {
  width: 100px; // 更小的宽度适应紧凑的布局
}

.el-tag {
  cursor: pointer;
  margin-bottom: 0; // 移除底部外边距
}

/*复选框*/
.selections {
  display: inline-block;
  width: 500px;
  margin-left: 30px;
}

/*时间输入框样式*/
.in_date {
  display: inline-block;
  width: 400px;
  margin-left: 100px;
  margin-top: 10px;
}

/*新增：生成图标按钮样式*/
.generate_button {
  display: inline-block;
  width: 100px;
  margin-left: 100px;
}

/*新增：下拉框选择展示类型样式*/
.display_type {
  display: inline-block;
  width: 130px;
  margin-left: 30px;
}

/*info的样式*/
.info {
  margin-top: -560px;
  margin-right: 60px;
  float: right;
  text-align: left;
  font-size: 13px; //字号
  text-indent: 20px; //缩进
  color: #5d5d5d;
  //background-color: #407e96;
  width: 260px;
  height: 300px;

  th, td {
    padding: 2px;
  }
}

/*node_info的样式*/
.node_info {
  float: right;
  margin-right: 20px;
  margin-top: -245px;
  text-align: left;
  text-indent: 20px; //缩进
  line-height: 1.8; //行距
  font-size: 13px; //字号
  color: #5d5d5d;
  background-color: #eeeeee;
  width: 280px;
  height: 240px;
  overflow-y: auto; // 添加自动显示垂直滚动条
}

//阈值控制器组件
.threshold-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

</style>