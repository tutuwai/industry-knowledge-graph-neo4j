<template>
  <div id="header" class="header">
    <!-- 搜索栏：仅包括搜索输入框 -->
    <div class="search-bar">
      <SearchComponent @search="handleSearch"/>
    </div>

    <!-- 显示搜索结果和搜索用时 -->
    <div v-if="searchResults.length">
      <div class="search-results-info">
        <h2>搜索结果：大约有 {{ searchTotal }} 项符合查询结果。（搜索耗时：{{ searchTime / 1000 }} 秒）</h2>
      </div>
      <div class="row">
        <div class="result-card" v-for="(result, index) in searchResults" :key="index">
          <h3><a :href="`#/patent/${result.公开号}`" target="_blank"
                 v-html="result.高亮 && result.高亮.名称 ? result.高亮.名称 : result.名称"></a></h3>
          <p v-html="result.高亮 && result.高亮.摘要 ? result.高亮.摘要 : result.摘要"></p>
          <div class="metadata">
            <span class="meta">公开号: {{ result.公开号 }}</span>
            <span class="meta">文献类型: {{ result.文献类型 }}</span>
            <span class="meta">公开日: {{ result.公开日 }}</span>
          </div>
          <p class="score">分数: {{ result._score }}</p>
        </div>
      </div>
    </div>
  </div>
  <button @click="prevPage" :disabled="currentPage <= 1">上一页</button>
  <button @click="nextPage" :disabled="currentPage >= totalPages">下一页</button>
</template>

<script>
import axios from 'axios';
import SearchComponent from '../components/ProfilePage/Search.vue';

export default {
  components: {
    SearchComponent,
  },
  data() {
    return {
      searchResults: [],
      searchTotal: 0,
      searchTime: 0,
      currentPage: 1,
      pageSize: 10,
      totalPages: 0,
      lastSearchText: '',  // 保存最后一次搜索文本
    };
  },
  methods: {
    async handleSearch(searchText) {
      this.lastSearchText = searchText;  // 保存搜索文本
      const apiEndpoint = `http://127.0.3.1:5001/search/patent?query=${encodeURIComponent(searchText)}&page=${this.currentPage}&page_size=${this.pageSize}`;
      const response = await axios.get(apiEndpoint);
      if (response.data) {
        this.searchResults = response.data.results;
        this.searchTotal = response.data.total;
        this.totalPages = Math.ceil(this.searchTotal / this.pageSize);
        this.searchTime = response.data.took;
      }
    },
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
        this.handleSearch(this.lastSearchText);
      }
    },
    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
        this.handleSearch(this.lastSearchText);
      }
    }
  }
};
</script>

<style scoped>
.header {
  margin-left: auto;
  margin-right: auto;
  width: 100%;
}

.search-bar {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  margin-bottom: 20px;
}

.search-results-info {
  margin-left: 5%; /* 设置与结果卡片相同的左边距 */
  margin-right: 5%; /* 设置与结果卡片相同的右边距 */
}

.result-card {
  padding: 20px;
  margin-bottom: 20px;
  margin-left: 5%;
  margin-right: 5%;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.result-card h3, .result-card p, .metadata {
  margin-bottom: 10px;
}

.result-card .metadata {
  font-size: 14px;
  color: #666;
}

.result-card .meta {
  display: block;
}

.result-card .score {
  font-size: 14px;
  color: #999;
  margin-top: 10px;
}
</style>
