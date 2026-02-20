<template>
  <div class="echart" id="mychart" :style="myChartStyle"></div>
</template>

<script>
import { markRaw } from 'vue';
import * as echarts from 'echarts';

export default {
  props: {
    data: {
      type: Object,
      required: true,
    },
    title: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      myChart: null,
      myChartStyle: { float: 'left', width: '100%', height: '100%' },
    };
  },
  watch: {
    data: {
      immediate: true,
      handler(newData) {
        if (this.myChart) {
          this.updateChart(newData);
        }
      },
    },
  },
  mounted() {
    this.initEcharts();
  },
  methods: {
    initEcharts() {
      this.myChart = markRaw(echarts.init(document.getElementById('mychart')));
      const option = {
        title: {
          text: this.title,
          left: 'center',
        },
        xAxis: {
          type: 'category',
          data: this.data.years,
        },
        legend: {
          data: ['专利数量', '专利重要度'],
          bottom: '0%',
        },
        yAxis: {},
        series: [
          {
            name: '专利数量',
            type: 'line',
            data: this.data.patentCounts,
            label: {
              show: true,
              position: 'top',
              textStyle: {
                fontSize: 16,
              },
              formatter: function (value) {
                return value.data.toFixed(2);
              },
            },
          },
          {
            name: '专利重要度',
            type: 'line',
            data: this.data.importanceScores,
            label: {
              show: true,
              position: 'bottom',
              textStyle: {
                fontSize: 16,
              },
              formatter: function (value) {
                return value.data.toFixed(2);
              },
            },
          },
        ],
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow',
          },
        },
      };
      this.myChart.setOption(option);
      window.addEventListener('resize', () => {
        this.myChart.resize();
      });

      this.myChart.on('click', (params) => {
        if (params.componentType === 'series') {
          this.$emit('yearClicked', params.name);
        }
      });
    },
    updateChart(newData) {
      this.myChart.setOption({
        title: {
          text: this.title,
        },
        xAxis: {
          data: newData.years,
        },
        series: [
          {
            name: '专利数量',
            data: newData.patentCounts,
            label: {
              formatter: function (value) {
                return value.data.toFixed(2);
              },
            },
          },
          {
            name: '专利重要度',
            data: newData.importanceScores,
            label: {
              formatter: function (value) {
                return value.data.toFixed(2);
              },
            },
          },
        ],
      });
    },
  },
};
</script>

<style scoped>
.echart {
  width: 100%;
  height: 100%;
}
</style>
