<template>
  <div class="top-controls">
    <!--复选框-->
    <div class="selections">
      <el-checkbox v-model="ipc" label="IPC" size="large"/>
      <el-checkbox v-model="patent" label="专利" size="large"/>
      <el-checkbox v-model="inventor" label="发明人" size="large"/>
      <el-checkbox v-model="agent" label="代理机构" size="large"/>
      <el-checkbox v-model="applicant" label="申请人" size="large"/>
    </div>
    <!--新增：下拉框选择展示类型-->
    <div class="display_type">
      <el-select v-model="displayMode" placeholder="请选择">
        <el-option label="普通模式" value="normal"></el-option>
        <el-option label="重要度模式" value="importance"></el-option>
      </el-select>
    </div>
    <!--结点颜色含义放置框：框内为各类结点对应颜色-->
    <div class="indicator-and-thresholds">
      <!-- 循环遍历names数组，为每个元素创建一个el-tag -->
      <div class="node-control" v-for="(name, index) in names" :key="index">
        <el-tag :style="{ backgroundColor: colors[index], color: 'white' }">
          {{ name }}
        </el-tag>
      </div>
    </div>
  </div>
  <!--图谱可视化区域-->
  <svg>
    <force-graph v-if="displayMode === 'normal'" :url="api1" v-on:clickNode="showNodeInfo" :Ipc="ipc" :Patent="patent"
                 :Inventor="inventor" :Agent="agent" :Applicant="applicant" :thresholds="thresholds" :current-date=
                     "time"
                 @update-statistics="handleStatisticsUpdate"/>
    <ForceGraph_pagerank v-if="displayMode === 'importance'" :url="api1" v-on:clickNode="showNodeInfo" :Ipc="ipc"
                         :Patent="Patent"
                         :Inventor="inventor" :Agent="agent" :Applicant="applicant" :thresholds="thresholds"
                         @update-statistics="handleStatisticsUpdate"/>
  </svg>
  <!--  图-->
  <div class="chart-container">
    <Node_num_line></Node_num_line>
  </div>
  <!-- 时间轴 -->
  <div class="timeline">
    <el-slider v-model="sliderYear" :min="2008" :max="2024" show-input step="1" @change="updateTime"></el-slider>
  </div>
  <!--生成图标按钮-->
  <div class="generate_button">
    <el-button type="primary" @click="updateGraph">更新图谱</el-button>
  </div>


</template>
<script>
import ForceGraph_pagerank from "../components/DynamicPage/ForceGraph_pagerank_D.vue";
import ForceGraph from "../components/DynamicPage/ForceGraph_D.vue";
import Node_num_line from "@/components/DynamicPage/Node_num_line.vue";


let bool_input = false;
export default {
  name: "HomePage",
  components: {ForceGraph, ForceGraph_pagerank, Node_num_line},
  data() {
    return {
      api1: "http://127.0.3.1:5001/datas?score_patent=3.5&score_agent=6&score_inventor=5&score_ipc=40&score_applicant=5",
      names: ["专利", '代理机构', '发明人', "IPC", "申请人"],
      colors: ['#6aabd1', '#fdae61', '#e76f51'
        , '#38dac1', '#f53064'],
      patent: true,
      agent: false,
      inventor: false,
      ipc: true,
      applicant: false,
      selectedNode: null,
      displayMode: "normal",
      nodeStatistics: {},
      timeValue: 0,
      sliderYear: 2008,
      time: '',
      thresholds: {
        patent: 3.5,
        agent: 6,
        inventor: 5,
        ipc: 40,
        applicant: 5
      },
    };
  },
  methods: {
    //更新结点状态信息
    handleStatisticsUpdate(statistics) {
      this.nodeStatistics = statistics;
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
    updateTime() {
      const currentYear = this.sliderYear;
      const currentDate = new Date(currentYear, 0, 1);  // 生成当前滑块年份的1月1日的日期对象

      if (!isNaN(currentDate.valueOf())) {
        // 构建日期字符串，格式为 xxxx.xx.xx
        let month = currentDate.getMonth() + 1;  // 获取月份，+1 是因为 getMonth() 返回的月份从0开始
        month = month < 10 ? '0' + month : month;  // 月份两位数表示
        let day = currentDate.getDate();  // 获取日
        day = day < 10 ? '0' + day : day;  // 日两位数表示

        this.time = `${currentYear}.${month}.${day}`;  // 拼接字符串
        console.log("Formatted date:", this.time);
      }
    },


    // 新增：更新图表方法
    updateGraph() {
      if (bool_input == false) {
        const params = {
          link: this.patent,
          patent: this.patent,
          inventor: this.inventor,
          start_time: "1900-1-1",
          end_time: "2024-1-1",
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
      console.log('clicked node:', node);
    },
  },
  computed: {
    sliderTimeValue: {
      get() {
        const startYear = 1900;
        const endYear = 2023;
        const currentYear = new Date(this.time).getFullYear();
        return ((currentYear - startYear) / (endYear - startYear)) * 100;
      },
      set(value) {
        this.timeValue = value;
      },
    },
  },


};
</script>

<style lang="less" scoped>
svg {
  width: 910px;
  height: 530px;
  background-color: #eee;
  margin-left: 10px;
  margin-top: 10px;
}


/* 移除 .chart-container 中所有未使用的注释 */

.selections, .display_type, .indicator {
  display: flex;
  align-items: center;
  flex-grow: 1; /* 让每个部分都有扩展的空间 */
  margin-right: 20px; /* 为每个部分之间添加一些间隔 */
}

.selections {
  flex-wrap: wrap; /* 如果复选框多，允许换行 */
  margin-left: 50px; /* 增加左边距，让复选框向右移动 */
}

.indicator {
  flex-grow: 2; /* 给颜色指示更多的扩展空间 */
}

.list_color {
  margin-right: 10px; /* 减少颜色块之间的间隔 */
}

.list_color span {
  white-space: nowrap; /* 防止标签内的文字换行 */
}

.generate_button {
  display: inline-block;
  margin-left: 30px;
}

.chart-container {
  margin-right: 100px;
  float: right;
  text-align: left;
  font-size: 13px; /* 字号 */
  text-indent: 20px; /* 缩进 */
  color: #9f1414;
  width: 300px;
  height: 300px;
}

.node-control {
  display: flex;
  align-items: center;
  margin-right: 10px; /* 根据需要调整 */
}

.el-tag {
  margin-right: 5px; /* 如果需要在标签和输入框之间增加空间 */
}

.timeline {
  display: inline-block;
  margin-left: 20px;
  width: 1000px;

  input[type="range"] {
    width: 100%;
  }
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

</style>