<template>
  <!-- 为 ECharts 准备一个具备大小（宽高）的 容器 -->
  <div ref="chartRef" :style="{ width: '100%', height: '100%', border: 'none', margin: '0' }"></div>
</template>

<script setup>
// eslint-disable-next-line
import { ref, watch, onMounted, onBeforeUnmount } from 'vue';
import * as echarts from 'echarts';

// eslint-disable-next-line
const props = defineProps({
  width: {
    type: String,
    default: '100%',
  },
  height: {
    type: String,
    default: '100%',
  },
  data: {
    type: Object,
    required: true,
  },
});

const chartRef = ref(null);
let chartInstance = null;

const initChart = () => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value);
  }
};

watch(
  () => props.data,
  (data) => {
    if (chartInstance) {
      const option = {
        backgroundColor: '#b9f6b9',
        title: {
          text: '专利价值雷达图',
          top: '0%',
          left: 'center',
          textStyle: {
            color: '#333',
            fontSize: 20,
          },
        },
        legend: {
          show: true,
          icon: 'rect',
          bottom: '0%', // 将图例移动到底部
          left: 'center',
          itemWidth: 14,
          itemHeight: 14,
          itemGap: 20,
          orient: 'horizontal',
          textStyle: {
            fontSize: 14,
            color: '#333',
          },
          data: [
            {
              name: '专利价值',
              icon: 'rect',
              textStyle: {
                color: '#333',
                fontWeight: 'bold',
              },
            },
          ],
        },
        tooltip: {
          show: true,
          trigger: 'item',
          formatter: function (params) {
            const values = params.value;
            return `
              <div style="padding: 10px; border-radius: 5px; background-color: rgba(255, 255, 255, 0.8); box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);">
                <div><strong>被引量:</strong> ${values[0]}</div>
                <div><strong>法律状态:</strong> ${values[1] ? '有效' : '无效'}</div>
                <div><strong>图重要度:</strong> ${values[2]}</div>
                <div><strong>相关专利数:</strong> ${values[3]}</div>
                <div><strong>时间价值:</strong> ${values[4]}</div>
              </div>
            `;
          },
        },
        radar: [
          {
            center: ['50%', '55%'],
            radius: '70%',
            startAngle: 90,
            name: {
              formatter: '{value}',
              textStyle: {
                fontSize: 16,
                color: '#333',
              },
            },
            nameGap: 10,
            splitNumber: 4,
            shape: 'circle',
            axisLine: {
              lineStyle: {
                color: '#ddd',
                width: 1,
                type: 'solid',
              },
            },
            splitLine: {
              lineStyle: {
                color: '#ddd',
                width: 1,
              },
            },
            splitArea: {
              show: true,
              areaStyle: {
                color: ['rgba(255,255,255,0.3)', 'rgba(200,200,200,0.3)'],
              },
            },
            indicator: [
              { name: '被引量', max: 15 },
              { name: '法律状态', max: 2 },
              { name: '图重要度', max: 10 },
              { name: '相关专利数', max: 100 },
              { name: '时间价值', max: 300 },
            ],
          },
        ],
        series: [
          {
            name: '专利价值',
            type: 'radar',
            itemStyle: {
              normal: {
                lineStyle: {
                  width: 2,
                },
                opacity: 0.5,
              },
              emphasis: {
                lineStyle: {
                  width: 4,
                },
                opacity: 1,
              },
            },
            data: [
              {
                name: '专利价值',
                value: [
                  data.citation_count || 0,
                  data.legal_status === '有效' ? 1 : 0,
                  data.page_rank_score || 0,
                  data.related_patent_count || 0,
                  data.time_value_score || 0,
                ],
                symbol: 'circle',
                symbolSize: 8,
                label: {
                  normal: {
                    show: true,
                    position: 'top',
                    distance: 2,
                    color: '#333',
                    fontSize: 12,
                    formatter(params) {
                      return params.value;
                    },
                  },
                },
                itemStyle: {
                  normal: {
                    borderColor: '#333',
                    borderWidth: 2,
                  },
                },
                lineStyle: {
                  normal: {
                    opacity: 0.5,
                  },
                },
                areaStyle: {
                  normal: {
                    color: 'rgba(51,0,255,0.3)',
                  },
                },
              },
            ],
          },
        ],
      };
      chartInstance.setOption(option);
    }
  },
  { immediate: true }
);

// 当组件挂载时初始化图表
onMounted(() => {
  initChart();
  if (!chartInstance) {
    console.error('ECharts instance was not initialized');
  }
});

// 当组件卸载时销毁图表实例
onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.dispose();
  }
});
</script>
