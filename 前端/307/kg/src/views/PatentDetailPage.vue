<template>
  <div class="patent-detail-page">
    <div class="graph-area">
      <force-graph-graph :url="apiUrl" @clickNode="showNodeInfo" :thresholds="thresholds"></force-graph-graph>
    </div>
    <div class="node-info">
      <div class="node_info" v-html="selectedNode ? selectedNodeInfo : ''"></div>
    </div>
    <div class="value-statistics">
      <visit-radar :loading="loading" :data="patentDetails"></visit-radar>
    </div>
    <div class="line-chart">
      <line-chart :data="lineChartData" :title="lineChartTitle" @yearClicked="handleYearClicked"></line-chart>
    </div>
    <pie-chart class="pie-chart" :id="'pieChart'" :title="pieChartTitle" :data="pieChartData"></pie-chart>
  </div>
</template>

<script>
import axios from 'axios';
import ForceGraphGraph from '../components/PatentDetailPage/ForceGraph_Graph.vue';
import VisitRadar from '../components/PatentDetailPage/VisitRadar.vue';
import LineChart from '../components/PatentDetailPage/LineChart.vue';
import PieChart from '../components/PatentDetailPage/PieChart.vue';

export default {
  name: 'PatentDetailPage',
  components: {
    ForceGraphGraph,
    VisitRadar,
    LineChart,
    PieChart,
  },
  data() {
    return {
      publicationNumber: this.$route.params.publicationNumber,
      selectedNode: null,
      thresholds: {
        patent: 1.0,
        agent: 0,
        inventor: 0,
        ipc: 0,
        applicant: 0,
      },
      displayMode: 'normal',
      patentDetails: null,
      loading: true,
      lineChartData: {
        years: [],
        patentCounts: [],
        importanceScores: [],
      },
      pieChartData: [],
      pieChartTitle: '',
      lineChartTitle: '专利数量和重要度趋势',
    };
  },
  computed: {
    apiUrl() {
      return `http://127.0.3.1:5001/search/patent_details?publication_number=${this.publicationNumber}`;
    },
    selectedNodeInfo() {
      const node = this.selectedNode;
      if (!node) {
        return '';
      }

      const nodeTypes = {
        0: '专利',
        1: '代理机构',
        2: '发明人',
        3: 'IPC分类号',
        4: '申请人',
      };

      let info = `<div>结点ID: ${node.id}</div>`;
      info += `<div>结点类型: ${nodeTypes[node.group]}</div>`;
      info += `<div>结点重要度: ${node.pageRankScore}</div>`;
      switch (node.group) {
        case 0:
          info += `
            <div>名称: ${node.名称}</div>
            <div>公开号: ${node.公开号}</div>
            <div>公开日: ${node.公开日}</div>
            <div>摘要: ${node.摘要}</div>
            <div>文献类型: ${node.文献类型}</div>
            <div>申请号: ${node.申请号}</div>
            <div>申请日: ${node.申请日}</div>
            <div><a href="#/patent/community/${node.公开号}" target="_blank">查看社群图</a></div>`; // 添加链接
          break;
        case 1:
          info += `<div> 名称: ${node.名称}</div>`;
          this.fetchRelatedPatents('代理机构', node.名称);
          break;
        case 2:
          info += `<div> 名称: ${node.名称}</div>`;
          this.fetchRelatedPatents('发明人', node.名称);
          break;
        case 3:
          info += `<div> 名称: ${node.名称}</div>
          `;
          this.fetchRelatedPatents('IPC', node.名称);
          break;
        case 4:
          info += `<div> 名称: ${node.名称}</div>
          <div>邮编: ${node.邮编}</div>`;
          this.fetchRelatedPatents('申请人', node.名称);
          break;
      }
      return info;
    },
  },
  mounted() {
    this.fetchPatentDetails();
  },
  methods: {
    showNodeInfo(node) {
      if (!node) {
        return;
      }
      this.selectedNode = node;
      this.updateLineChartTitle(node);
    },
    updateLineChartTitle(node) {
      const nodeName = node.名称 || node.id;
      this.lineChartTitle = `${nodeName}
          的专利数量和重要度趋势`;
    },
    async fetchPatentDetails() {
      this.loading = true;
      try {
        const response = await fetch(`
          http://127.0.3.1:5001/patent_info?publication_number=${this.publicationNumber}`);
        const data = await response.json();
        console.log('API response data:', data);
        this.patentDetails = data;
      } catch
          (error) {
        console.error('Error fetching patent details:', error);
      } finally {
        this.loading = false;
      }
    },
    async fetchRelatedPatents(entityType, name) {
      try {
        const response = await axios.get('http://127.0.3.1:5001/search/related_patents', {
          params: {
            entity_type: entityType,
            name: name,
          },
        });
        const data = response.data.data;

        const yearData = {};
        data.forEach((item) => {
          const year = item.专利年份;
          if (!yearData[year]) {
            yearData[year] = {count: 0, importanceSum: 0};
          }
          yearData[year].count += 1;
          yearData[year].importanceSum += item.专利重要度;
        });

        const years = Object.keys(yearData).sort();
        const patentCounts = years.map((year) => yearData[year].count);
        const importanceScores = years.map((year) => yearData[year].importanceSum);

        this.lineChartData = {
          years,
          patentCounts,
          importanceScores,
          allData: data,
        };
      } catch (error) {
        console.error('Error fetching related patents:', error);
      }
    },
    handleYearClicked(year) {
      const yearData = this.lineChartData.allData.filter((item) => item.专利年份 === year);
      const totalImportance = yearData.reduce((acc, item) => acc + item.专利重要度, 0);

      const pieChartData = yearData.map((item) => ({
        name: item.专利名称,
        value: (item.专利重要度 / totalImportance) * 100,
        专利重要度: item.专利重要度,
      }));

      this.pieChartData = pieChartData;
      this.pieChartTitle = `${year} 年的专利重要度占比`;

      console.log('Pie chart data:', this.pieChartData);
    },
  },
};
</script>

<style scoped>
.patent-detail-page {
  display: grid;
  grid-template-columns: 5fr 2fr;
  grid-template-rows: repeat(7, 1fr);
  gap: 20px;
  padding: 20px;
  height: 100vh;
  background-color: #f0f0f0;
}

.graph-area,
.node-info,
.value-statistics,
.line-chart,
.pie-chart {
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #ccc;
}

.graph-area {
  grid-column: 1 / 2;
  grid-row: 1 / 5;
  background-color: #ffffff;
  overflow: hidden;
  position: relative;
}

.graph-area svg {
  width: 100%;
  height: 100%;
}

.node-info {
  grid-column: 2 / 3;
  grid-row: 1 / 2;
  background-color: #aaaaf1;
}

.value-statistics {
  grid-column: 2 / 3;
  grid-row: 2 / 5;
  background-color: #b9f6b9;
}

.line-chart {
  grid-column: 1 / 2;
  grid-row: 5 / 8;
  background-color: #fee;
}

.pie-chart {
  grid-column: 2 / 3;
  grid-row: 5 / 8;
  background-color: #ffffff;
}

.node-info {
  grid-column: 2 / 3;
  grid-row: 1 / 2;
  background-color: #aaaaf1;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #ccc;
  overflow-y: auto;
  max-height: 100%;
}
</style>
