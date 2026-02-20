<template>
  <div class="search-box">
    <!-- 搜索输入框 -->
    <input type="text" v-model="searchText" placeholder="请输入搜索内容" />

    <!-- 确定按钮 -->
    <button @click="submitSearch">搜索</button>
  </div>
</template>

<script>
export default {
  name: 'ProfileSearch',  // 更新组件名
  data() {
    return {
      searchText: '', // 绑定到输入框的数据
    };
  },
  methods: {
    submitSearch() {
      this.$emit('search', this.searchText); // 当点击搜索按钮时，向父组件发送一个带有搜索文本的事件
    },
  },
};
</script>

<style scoped>
/*.search-box {*/
/*  margin-bottom: 20px;*/
/*}*/

.search-box input {
  width: 500px; /* 增大输入框的宽度 */
  height: 36px; /* 增大输入框的高度 */
  font-size: 18px; /* 增大输入框的字体大小 */
}

.search-box button {
  height: 36px;
  margin-left: 10px;
}
</style>
