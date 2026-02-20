<template>
  <div ref="chartDom" style="width: 400px; height: 580px;"></div>
</template>

<script>
import {ref, onMounted} from 'vue';
import * as echarts from 'echarts';

export default {
  setup() {
    const chartDom = ref(null);
    let chartInstance = null;

    onMounted(() => {
      chartInstance = echarts.init(chartDom.value);

      const option = {
            legend: {},
            tooltip: {
              trigger: 'axis',
              showContent: false
            },
            dataset: {
              source: [
                ['product', '2004', '2005', '2006', '2007', '2008', '2009', '2010',
                  '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018',
                  '2019', '2020', '2021', '2022', '2023', '2024'],
                ['专利', '14', '18', '29', '38', '66', '109', '157', '221', '327', '492', '638', '821',
                  '1083', '1373', '1850', '2320', '2928', '3804', '4700', '5555', '5803'],
                ['专利与发明人', '27', '42', '66', '110', '265', '440', '637', '847', '1265', '1901', '2474',
                  '3268', '4364', '5842', '8011', '10564', '14014', '19172', '24766', '30553', '32349'],
                ['专利与ipc', '24', '37', '56', '77', '154', '268', '411', '560', '765', '1065', '1382', '1744',
                  '2360', '3107', '4244', '5461', '7404', '10598', '14002', '17397', '18406'],
                ['专利与申请人', '15', '20', '31', '40', '71', '119', '178', '251', '364', '568', '737', '954',
                  '1254', '1600', '2157', '2744', '3477', '4605', '5797', '6965', '7305'],
                ['专利与代理机构', '12', '15', '23', '31', '56', '96', '130', '174', '247', '375', '489', '630',
                  '825', '1055', '1456', '1868', '2374', '3137', '3951', '4744', '4977'],
                ['专利与专利', '1', '2', '4', '6', '25', '57', '81', '109', '157', '262', '324', '425',
                  '509', '640', '845', '1023', '1200', '1334', '1397', '1414', '1414']
              ]
            },
            xAxis: {
              type: 'category'
            }
            ,
            yAxis: {
              gridIndex: 0
            }
            ,
            grid: {
              top: '55%' //表格纵
            }
            ,
            series: [
              {
                type: 'line',
                smooth: true,
                seriesLayoutBy: 'row',
                emphasis: {focus: 'series'}
              },
              {
                type: 'line',
                smooth: true,
                seriesLayoutBy: 'row',
                emphasis: {focus: 'series'}
              },
              {
                type: 'line',
                smooth: true,
                seriesLayoutBy: 'row',
                emphasis: {focus: 'series'}
              },
              {
                type: 'line',
                smooth: true,
                seriesLayoutBy: 'row',
                emphasis: {focus: 'series'}
              },
              {
                type: 'line',
                smooth: true,
                seriesLayoutBy: 'row',
                emphasis: {focus: 'series'}
              },
              {
                type: 'line',
                smooth: true,
                seriesLayoutBy: 'row',
                emphasis: {focus: 'series'}
              },
              {
                type: 'pie',
                id: 'pie',
                radius: '40%',//圆饼大小
                center: ['48%', '30%'],//横坐标，纵坐标
                emphasis: {
                  focus: 'self'
                },
                label: {
                  formatter: '{b}: {@2012} ({d}%)'
                },
                encode: {
                  itemName: 'product',
                  value: '2012',
                  tooltip: '2012'
                }
              }
            ]
          }
      ;

      chartInstance.setOption(option);

      chartInstance.on('updateAxisPointer', function (event) {
        const xAxisInfo = event.axesInfo[0];
        if (xAxisInfo) {
          const dimension = xAxisInfo.value + 1;
          chartInstance.setOption({
            series: {
              id: 'pie',
              label: {
                formatter: '{b}: {@[' + dimension + ']} ({d}%)'
              },
              encode: {
                value: dimension,
                tooltip: dimension
              }
            }
          });
        }
      });
    });

    return {chartDom};
  },
};
</script>
