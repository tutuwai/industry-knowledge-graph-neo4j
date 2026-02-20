<template>
  <div class="echarts-map-china" ref="echarts-map-china"></div>

  <div class="echarts-pie">
    <PieChart :data="options.pieChartData" :title="Pietitle"/>
  </div>
  <div class="analysis">
    <BarChart :data="options.stackedLineChartData" :title="Linetitle"></BarChart>
  </div>
</template>
<script>
import "@/utils/china"
import * as echarts from 'echarts';
import axios from 'axios';
import BarChart from "../MapPage/BarChart.vue";
import PieChart from "../MapPage/PieChart.vue";

export default {
  components: {BarChart, PieChart},
  props: {
    api: {
      type: String,
      required: true,
    },
    api_summary: {
      type: String,
      required: true,
    },
    type: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      api1: "",
      myEcharts: null,
      options: {
        title: {
          text: '专利地图分布',
          x: "center",
          textStyle: {
            fontSize: 19,
            color: "black"
          },
        },
        tooltip: {
          trigger: 'item',
          backgroundColor: "white",
          formatter: ''
        },
        visualMap: {
          top: '55%',
          left: '6%',
          min: 0,
          max: 50,
          text: ['High', 'Low'],
          realtime: true,
          calculable: true,
          inRange: {
            color: ['#dfebff', '#012bfb']
          }
        },
        series: [
          {
            name: '模拟数据',
            type: 'map',
            mapType: 'china',
            roam: true,
            itemStyle: {
              normal: {
                label: {
                  show: true,
                  textStyle: {
                    color: "black"
                  }
                }
              },
              zoom: 1.5,
              emphasis: {
                label: {show: true}
              }
            },
            top: "5%",
            data: []
          }
        ],
        pieChartData: [],  // 初始化为一个空数组
        Linetitle: "",
        Pietitle: "",
        stackedLineChartData: [],  // 初始化为一个空数组
        companyData: [],  // 初始化为一个空数组
        relationData: [],  // 初始化为一个空数组
        productData: [],  // 初始化为一个空数组
      }
    };
  },

  mounted() {
    this.myEcharts = echarts.init(this.$refs["echarts-map-china"]);
    this.updateOptions();
    this.loadData();
    // 监听地图点击事件
    this.myEcharts.on('click', this.handleMapClick);
  },
  watch: {
    api: {
      handler: function () {
        this.updateOptions();
        this.loadData();
      },
      deep: true,
    },
    api_summary: {  // 新增对 api_summary 的观察
      handler: function () {
        this.updateOptions();
        this.loadData();
      },
      deep: true,
    },
    type: {
      handler: function () {
        this.updateOptions();
        this.loadData();
      },
      deep: true,
    },
  },
  methods: {
    // 转换数据以适配图表
    transformDataForChart(data, type) {
      const transformed = [];
      Object.keys(data).forEach(province => {
        data[province].forEach(item => {
          const existing = transformed.find(entry => entry.name === item.name);
          if (existing) {
            existing[type] = item.value;
          } else {
            transformed.push({name: item.name, 专利: 0, 申请人: 0, 发明人: 0, [type]: item.value});
          }
        });
      });
      return transformed;
    },
    updateOptions() {
      this.options.tooltip.formatter = `地区：{b}<br/>${this.type}：{c}`;
    },
    // 修改 handleMapClick 方法
    handleMapClick(params) {
      const provinceName = params.name; // 获取点击的省份名称
      this.setVisualData(provinceName); // 根据省份设置数据
    }
    ,
    loadData() {
      // 加载地图数据
      axios.get(this.api).then(response => {
        if (response.data.status === 'success') {
          const data = response.data.results[this.type]; // 从 api 获取地图数据
          this.options.visualMap.max = Math.max(...data.map(item => item.value)) || 50; // 更新视觉映射的最大值
          this.options.series[0].data = data;
          this.myEcharts.setOption(this.options, true); // 更新地图数据
        } else {
          console.error('地图数据请求失败:', response.data.message);
        }
      }).catch(error => {
        console.error('地图数据请求错误:', error);
      });
      console.error('地图数据:', this.type);
      console.error('地图数据:', this.options.series[0].data);

      // 加载圆饼图和柱状图数据
      axios.get(this.api_summary).then(response => {
        if (response.data.status === 'success') {
          const summaryData = response.data.results; // 获取综合数据
          this.companyData = summaryData.applicant;
          this.relationData = summaryData.inventor;
          this.productData = summaryData.patent;
          this.pieChartData = summaryData.ipc;
          this.setVisualData('北京'); // 默认展示北京的数据
        } else {
          console.error('综合数据请求失败:', response.data.message);
        }
      }).catch(error => {
        console.error('综合数据请求错误:', error);
      });
    },
    // 设置视觉数据
    // 设置视觉数据
    setVisualData(provinceName) {
      // 检查数据是否已加载
      if (!this.pieChartData || !this.companyData || !this.relationData || !this.productData) {
        console.error("Data not loaded yet");
        return; // 数据未加载，直接返回
      }
      // 更新标题
      this.Pietitle = `${provinceName}省IPC构成`;
      this.Linetitle = `${provinceName}省专利分析`;
      // 直接引用对应省份的数据
      const pieData = this.pieChartData[provinceName] || [];
      const applicantData = this.companyData[provinceName] || [];
      const inventorData = this.relationData[provinceName] || [];
      const patentData = this.productData[provinceName] || [];

      // 更新饼图数据
      this.options.pieChartData = pieData;

      // 准备柱状图数据
      const stackedData = [];
      applicantData.forEach(item => {
        stackedData.push({
          name: item.name,
          专利: 0,
          申请人: item.value,
          发明人: 0
        });
      });

      inventorData.forEach(item => {
        const entry = stackedData.find(e => e.name === item.name);
        if (entry) {
          entry.发明人 = item.value;
        } else {
          stackedData.push({
            name: item.name,
            专利: 0,
            申请人: 0,
            发明人: item.value
          });
        }
      });

      patentData.forEach(item => {
        const entry = stackedData.find(e => e.name === item.name);
        if (entry) {
          entry.专利 = item.value;
        } else {
          stackedData.push({
            name: item.name,
            专利: item.value,
            申请人: 0,
            发明人: 0
          });
        }
      });

      this.options.stackedLineChartData = stackedData;

      // // 更新图表显示
      // this.myEcharts.setOption({
      //   series: [{
      //     data: this.options.pieChartData
      //   }, {
      //     data: this.options.stackedLineChartData
      //   }]
      // }, true); // 使用 true 参数强制覆盖以前的配置
    },
  }
};
</script>
<style lang="less" scoped>
.echarts-map-china {
  float: left;
  //background-color: darkmagenta;
  margin-top: 20px;
  margin-left: 10px;
  margin-bottom: 6px;
  height: 600px;
  width: 800px;
}

.echarts-pie {
  float: right;
  width: 480px;
  height: 300px;
  //background-color: #1907bb;
  margin-right: 10px;
  margin-top: 20px;
}

.analysis {
  float: right;
  width: 480px;
  height: 290px;
  //background-color: #44dab7;
  margin-bottom: 6px;
  margin-right: 10px;
  margin-top: 10px;
}
</style>
