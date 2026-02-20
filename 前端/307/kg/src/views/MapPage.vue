<template>
  <div>
    <china-map :api="api" :api_summary="api_summary" :type="selectedType"/>
  </div>
  <!-- 复选框 -->
  <!-- 时间范围输入查询 -->
  <div class="in_date">
    <date-picker v-model="dateRange" @update:value="handleDatepickerChange"/>
  </div>
  <!-- 新增：下拉框选择展示类型 -->
  <div class="display_type">
    <el-select v-model="selectedType" placeholder="请选择">
      <el-option label="重要度" value="重要度"></el-option>
      <el-option label="专利数量" value="专利数量"></el-option>
    </el-select>
  </div>
  <!-- 新增：生成图标按钮 -->
  <div class="generate_button">
    <el-button type="primary" @click="updateGraph">更新地图</el-button>
  </div>
</template>

<script>
import ChinaMap from "@/components/MapPage/ChinaMap.vue";
import DatePicker from "../components/common/DatePicker.vue";
import moment from "moment";

export default {
  name: "FourthPage",
  components: {ChinaMap, DatePicker},
  data() {
    return {
      api: "",
      api_summary: "",
      dateRange: [],
      start_time: "1990-10-10",
      end_time: "2020-2-1",
      selectedType: "专利数量",
    };
  },
  methods: {
    handleDatepickerChange(value) {
      this.end_time = moment(value).format("YYYY-MM-DD");
    },
    // 更新图表方法
    updateGraph() {
      // 简化 API，只使用时间参数
      this.api = `http://127.0.3.1:5001/datas/location?time=${this.end_time}`;
      this.api_summary = `http://127.0.3.1:5001/datas/location_summary?time=${this.end_time}`;

      console.log("Updated API URL:", this.api);
      console.log("Updated Company API URL:", this.api_summary);
    },
  },
  mounted() {
    this.updateGraph();
  },
}
</script>

<style lang="less" scoped>
/*时间输入框样式*/
.in_date {
  float: left;
  width: 400px;
  height: 40px;
  margin-left: 135px; /* 减小左边距使元素向左移 */
  margin-top: -30px;
}

/*新增：下拉框选择展示类型样式*/
.display_type {
  float: left;
  width: 200px;
  height: 40px;
  margin-top: -30px;
  margin-left: 10px; /* 减小左边距 */
}

/*新增：生成图标按钮样式*/
.generate_button {
  float: left;
  margin-left: 10px; /* 减小左边距 */
  margin-top: -30px;
}

.loading {
  /* 加载界面的样式 */
}
</style>
