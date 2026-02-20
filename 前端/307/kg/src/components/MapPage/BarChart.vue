<template>
  <div ref="chartRef" class="stacked-line-chart"></div>
</template>

<script>
import {onMounted, ref, watchEffect} from "vue";
import * as echarts from "echarts";

export default {
  name: "StackedLineChart",
  props: {
    id: {
      type: String,
      default: "",
    },
    title: {
      type: String,
      required: true,
    },
    data: {
      type: Array,
      required: true,
    },
  },
  setup(props) {
    const chartRef = ref(null);
    let myChart = null;

    onMounted(() => {
      myChart = echarts.init(chartRef.value);
      renderChart();
    });

    watchEffect(() => {
      console.log('props.data:', props.data);
      if (props.data.length && myChart) {
        renderChart();
      }
    });

    function renderChart() {
      myChart.clear(); // 清除之前的图表数据

      const seriesData = props.data.map(item => ({
        name: item.name.length > 5 ? item.name.substring(0, 5) + '...' : item.name, // 如果名称超过5个字符，则截取前5个字符并添加省略号
        type: 'bar',
        stack: '总量',
        data: [item.专利, item.申请人, item.发明人] // 确保数据按照'专利', '申请人', '发明人'的顺序
      }));

      const option = {
        title: {
          text: props.title,
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          },
          formatter: function (params) {
            let result = params[0].axisValueLabel + '<br>';
            params.forEach(param => {
              if (param.value > 0) {
                result += `${param.marker} ${param.seriesName}: ${param.value}<br>`;
              }
            });
            return result;
          },
        },
        legend: {
          show: false  // 隐藏图例
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: ['专利', '申请人', '发明人']
        },
        yAxis: {
          type: 'value'
        },
        series: seriesData
      };

      myChart.setOption(option);
    }


    return {
      chartRef,
    };
  },
};
</script>

<style scoped>
.stacked-line-chart {
  width: 440px;
  height: 260px;
}
</style>
