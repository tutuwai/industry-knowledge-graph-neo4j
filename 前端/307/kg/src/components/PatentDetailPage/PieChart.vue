<template>
  <div ref="chartRef" :id="id" class="pie-chart"></div>
</template>

<script>
import { onMounted, ref, watchEffect } from 'vue';
import * as echarts from 'echarts';

export default {
  name: 'PieChart',
  props: {
    id: {
      type: String,
      default: '',
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
      if (props.data.length && myChart) {
        renderChart();
      }
    });

    function renderChart() {
      console.log('Pie chart received data:', props.data);

      const option = {
        title: {
          text: props.title,
          left: 'center',
        },
        tooltip: {
          trigger: 'item',
          formatter: (params) => {
            return `${params.name}<br/>专利重要度: ${params.data.专利重要度.toFixed(2)}<br/>专利重要度占比: ${params.value.toFixed(2)}%`;
          },
        },
        series: [
          {
            name: '专利重要度占比',
            type: 'pie',
            top: '0%',
            data: props.data.map((item) => ({
              value: item.value,
              name: item.name,
              专利重要度: item.专利重要度,
            })),
          },
        ],
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
.pie-chart {
  width: 90%;
  height: 90%;
}
</style>
