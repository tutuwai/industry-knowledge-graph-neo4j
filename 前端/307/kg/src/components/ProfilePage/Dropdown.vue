<template>
  <div class="dropdown">
    <!-- 下拉框 -->
    <select v-model="selectedOption">
      <option value="title">标题</option>
      <option value="content">全文</option>
    </select>
  </div>
</template>

<script>
export default {
  name: 'ProfileDropdown',  // 更新组件名
  data() {
    return {
      selectedOption: 'title', // 默认选择“标题”
    };
  },
  watch: {
    selectedOption(newValue) {
      this.$emit('optionSelected', newValue); // 当选项发生改变时，向父组件发送一个带有新选项值的事件
    },
  },
};
</script>

<style>
.dropdown select {
  width: 100px; /* 或者你希望的任何宽度 */
  height: 36px; /* 和搜索框的高度相同 */
  font-size: 18px; /* 和搜索框的字体大小相同 */
  margin-right: 10px; /* 添加右边距 */
}
</style>
