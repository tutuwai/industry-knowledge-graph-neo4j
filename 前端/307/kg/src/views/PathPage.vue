<template>
  <div class="container">
    <div class="top-controls">
      <!-- 起点搜索区 -->
      <div class="search-box">
        <el-select v-model="startType" placeholder="选择起点类型" class="select-input">
          <el-option v-for="type in nodeTypes" :key="type.value" :label="type.label" :value="type.value"></el-option>
        </el-select>
        <input placeholder="请输入起点名称" type="text" v-model="inputStart" class="text-input">
      </div>
      <!-- 终点搜索区 -->
      <div class="search-box">
        <el-select v-model="endType" placeholder="选择终点类型" class="select-input">
          <el-option v-for="type in nodeTypes" :key="type.value" :label="type.label" :value="type.value"></el-option>
        </el-select>
        <input placeholder="请输入终点名称" type="text" v-model="inputEnd" class="text-input">
      </div>
      <el-button type="primary" @click="updateGraph">查询</el-button>
    </div>
    <!-- 结点类型和颜色指示 -->
    <div class="node-indicators">
      <div class="node-control" v-for="(name, index) in names" :key="index">
        <el-tag :style="{ backgroundColor: colors[index], color: 'white' }">{{ name }}</el-tag>
      </div>
    </div>
    <!-- 图表显示区 -->
    <div class="graph-container">
      <force-graph v-if="url && shouldLoadGraph" :url="url" :current-date="currentDate"
                   :thresholds="thresholds" :Ipc="Ipc" :Patent="Patent"
                   :Inventor="Inventor" :Agent="Agent" :Applicant="Applicant"
                   @update-statistics="handleStatisticsUpdate"/>
    </div>
    <!-- 结点类型选择区 -->
    <div class="checkboxes">
      <el-checkbox v-model="Ipc" label="IPC" size="large"/>
      <el-checkbox v-model="Patent" label="专利" size="large"/>
      <el-checkbox v-model="Inventor" label="发明人" size="large"/>
      <el-checkbox v-model="Agent" label="代理机构" size="large"/>
      <el-checkbox v-model="Applicant" label="申请人" size="large"/>
    </div>
  </div>
</template>

<script>
import ForceGraph from "@/components/PathPage/ForceGraph_D.vue";

export default {
  name: "PathFindingPage",
  components: {
    ForceGraph
  },
  data() {
    return {
      url: "",
      names: ["专利", '代理机构', '发明人', "IPC", "申请人"],
      colors: ['#6aabd1', '#fdae61', '#e76f51', '#38dac1', '#f53064'],
      nodeTypes: [
        { label: '专利', value: 'Patent' },
        { label: '代理机构', value: 'Agent' },
        { label: '发明人', value: 'Inventor' },
        { label: 'IPC', value: 'IPC' },
        { label: '申请人', value: 'Applicant' }
      ],
      inputStart: "",
      inputEnd: "",
      startType: "",
      endType: "",
      Ipc: true,
      Patent: true,
      Inventor: true,
      Agent: true,
      Applicant: true,
      currentDate: '2025-01-01',
      thresholds: {
        patent: 0,
        agent: 0,
        inventor: 0,
        ipc: 0,
        applicant: 0
      },
      shouldLoadGraph: false
    };
  },
  methods: {
    updateGraph() {
      if (this.inputStart && this.inputEnd && this.startType && this.endType) {
        this.url = `http://127.0.3.1:5001/search/shortest_paths?start_name=${this.inputStart}&end_name=${this.inputEnd}&start_label=${this.startType}&end_label=${this.endType}`;
        console.log("Updated API URL:", this.url);
        this.shouldLoadGraph = true;
      } else {
        this.shouldLoadGraph = false;
        console.log("Please fill in all search fields.");
      }
    },
    handleStatisticsUpdate(statistics) {
      console.log('Updated statistics:', statistics);
    }
  }
}
</script>

<style scoped>
.container {
  display: grid;
  grid-template-rows: repeat(7, 1fr);
  grid-template-columns: repeat(5, 1fr);
  height: 100vh;
}

/* 输入区和搜索按钮样式 */
.top-controls {
  grid-row: 1 / 2;
  grid-column: 1 / 4;
  display: flex;
  align-items: center;
  justify-content: space-around;
}

.search-box {
  display: flex;
  align-items: center;
}

.select-input {
  width: 120px;
  margin-right: 10px;
}

.text-input {
  width: 150px;
  margin-left: 10px;
  padding: 5px;
  font-size: 16px;
}

/* 结点颜色标签样式 */
.node-indicators {
  grid-row: 1 / 2;
  grid-column: 4 / 5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.node-control {
  margin-right: 5px;
}

/* 图表显示区 */
.graph-container {
  grid-row: 2 / 7;
  grid-column: 1 / 5;
}

/* 结点类型选择区 */
.checkboxes {
  grid-row: 7 / 8;
  grid-column: 2 / 4;
  display: flex;
  justify-content: space-around;
  align-items: center;
}
</style>
