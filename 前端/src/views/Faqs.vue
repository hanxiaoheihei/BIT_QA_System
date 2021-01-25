<template>
  <el-card class="container">
    <div slot="header">
      <span class="title">FAQ 数据</span>
    </div>
    <el-table
      class="list"
      :data="tableData"
      height="500"
      border
      v-loading="tableLoading"
      stripe
    >
      <el-table-column
        prop="q"
        label="问题"
        show-overflow-tooltip
      ></el-table-column>
      <el-table-column
        prop="a"
        label="答案"
        show-overflow-tooltip
      ></el-table-column>
    </el-table>
  </el-card>
</template>

<script>
import { fetchFaqs } from '@/api';

export default {
  name: 'faqs',
  data() {
    return {
      tableData: [],
      tableLoading: true,
    };
  },
  methods: {
    fetchData() {
      fetchFaqs().then((res) => {
        this.tableData = res.data.data;
        this.tableLoading = false;
      });
    },
  },
  mounted() {
    this.fetchData();
  },
};
</script>

<style>
.el-tooltip__popper {
  max-width: 50%;
}
</style>
