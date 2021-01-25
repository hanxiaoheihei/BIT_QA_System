<template>
    <el-card class="container">
        <div slot="header">
        <span class="title">Open QA</span>
        <el-button
            type="text"
            @click="showTips = !showTips"
            style="float: right; padding: 5px 0;"
            >排序</el-button
        >
        </div>

        <el-table
            :data="tableData"
            height="250"
            style="width: 100%"
            :default-sort = "{prop: 'question_id', order: 'ascending'}"
            >
			<el-table-column
            prop="question_id"
            label="文章ID"
            sortable
            width="90"
            :sort-method="sortChanges"
            >
			<template slot-scope="scope">
    			<a :href="scope.row.source_link">{{scope.row.question_id}}</a>
  			</template>
			</el-table-column>
            <el-table-column
            prop="final_prob"
            label="得分"
            sortable
            width="180"
            :sort-method="sortChange1"
            >
            </el-table-column>
            <el-table-column
            prop="answer"
            label="答案"
            width="540">
            </el-table-column>
        </el-table>

    </el-card>   
    
</template>

<script>
const axios = require('axios');

  export default {
    data() {
      return {
        tableData: []
      }
    },
    methods: {
      formatter(row, column) {
        return row.address;
      },
      open() {
        this.$prompt('请输入问题', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
        }).then(({ value }) => {
          this.$message({
            type: 'success',
            message: '你的问题是: ' + value
          });
          console.log(value)
          let data = {"send":new Date().toISOString()+ Math.random().toString(36).substr(2).toUpperCase(),"message":value}
          axios.post('http://127.0.0.1:7892/api/chat', data)
          .then((res) => {
            this.tableData = res.data.results
            console.log(this.tableData)
          })
        }).catch(() => {
          this.$message({
            type: 'info',
            message: '取消输入'
          });       
        });
      },
      sortChange1(a, b){
        return a.final_prob-b.final_prob;
      },
	  sortChange2(a, b){
        return a.question_id-b.question_id; 
      },    },
    created() {
        this.open()
    }
  }
</script>

<style>
</style>