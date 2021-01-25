<template>
  <el-card class="container">
    <div slot="header">
      <span class="title">文档管理</span>
      <el-button
        type="text"
        @click="dialogVisible = true"
        style="float: right; padding: 3px 0;"
        >上传</el-button
      >
    </div>
    <el-button
        type="text"
        @click="askDialogVisible = true"
        style="float: right; padding: 3px 0;"
        >提问</el-button
      >
    </div>
    <el-table
      class="list"
      :data="tableData"
      height="500"
      border
      v-loading="tableLoading"
    >
      <el-table-column prop="title" label="文档列表"></el-table-column>
      <el-table-column label="操作" width="200">
        <template slot-scope="scope">
          <el-popover
            placement="left"
            width="300"
            :content="start_and_end(scope.row.text)"
            trigger="hover"
            style="margin-right: 10px;"
          >
            <el-button type="text" size="small" slot="reference"
              >预览</el-button
            >
          </el-popover>
          <el-button type="text" size="small" @click="removeDoc(scope.row)"
            >删除</el-button
          >
          <el-button type="text" size="small" @click="ask(scope.row)"
            >提问</el-button
          >
        </template>
      </el-table-column>
    </el-table>
    <el-dialog title="上传文档" :visible.sync="dialogVisible" width="700px">
      <el-form ref="form" :model="form" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="form.title"></el-input>
        </el-form-item>
        <el-form-item label="内容">
          <el-input
            type="textarea"
            :rows="10"
            placeholder="请输入内容"
            v-model="form.content"
          ></el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="upload" :loading="uploadLoading"
          >上 传</el-button
        >
      </span>
    </el-dialog>
    <el-dialog
      title="对文档提问"
      :visible.sync="askDialogVisible"
      width="700px"
      @close="currentAnswer = currentQuestion = ''"
    >
    <el-form ref="form" :model="form" label-width="80px">
        <el-form-item label="内容">
          <el-input
            type="textarea"
            :rows="10"
            placeholder="请输入内容"
            v-model="form.content"
          ></el-input>
        </el-form-item>
        </el-form-item>
      </el-form>
      <el-form ref="form1" :model="form1" label-width="80px">
        <el-form-item label="答案">
          <el-input
            type="textarea"
            :rows="1"
            placeholder="请输入内容"
            v-model="form1.content"
          ></el-input>
        </el-form-item>
        </el-form-item>
      </el-form>
      <el-alert
        v-if="currentQuestion"
        title="问题"
        type="info"
        :description="currentQuestion"
        :closable="false"
        style="margin-top: -20px; margin-bottom: 10px;"
      >
      </el-alert>
      <div v-html="askHtml" class="display-area"></div>
      <el-input
        v-model="input"
        placeholder="请输入内容"
        @keyup.enter.native="sendMessage(input)"
      >
        <template slot="append">
          <el-button @click="sendMessage(input)" :loading="pending"
            >提问</el-button
          >
        </template>
      </el-input>
    </el-dialog>
  </el-card>
</template>

<script>
import {
  uploadDoc, fetchDocs, removeDoc, docAsk,
} from '@/api';

export default {
  name: 'upload',
  data() {
    return {
      tableData: [],
      content: '',
      dialogVisible: false,
      uploadLoading: false,
      form: {
        content: '',
        title: new Date().toLocaleString(),
      },
      form1: {
        content: '',
        title: new Date().toLocaleString(),
      },
      tableLoading: true,
      askDialogVisible: false,
      currentDoc: { text: '' },
      currentAnswer: '',
      currentQuestion: '',
      input: '',
      pending: false,
    };
  },
  computed: {
    askHtml() {
      if (this.currentAnswer) {
        return this.currentDoc.text.replace(this.currentAnswer, `<span style="background: #ffff00;">${this.currentAnswer}</span>`);
      }
      return this.currentDoc.text;
    },
  },
  methods: {
    upload() {
      this.uploadLoading = true;
      uploadDoc(this.form.title, this.form.content).then((res) => {
        this.uploadLoading = false;
        this.dialogVisible = false;
        if (res.data.code === 0) {
          this.$message.success('成功');
          this.fetchDocs();
        } else {
          this.$message.error(res.data.message);
        }
      });
    },
    fetchDocs() {
      fetchDocs().then((res) => {
        this.tableData = res.data.data;
        this.tableLoading = false;
      });
    },
    removeDoc(row) {
      // eslint-disable-next-line
      removeDoc(row._id).then(res => {
        if (res.data.code === 0) {
          this.$message.success('删除成功');
          this.fetchDocs();
        } else {
          this.$message.error(res.data.message);
        }
      });
    },
    start_and_end(str) {
      if (str.length > 100) {
        return `${str.substr(0, 180)}......`;
      }
      return str;
    },
    ask(row) {
      this.askDialogVisible = true;
      this.currentDoc = row;
    },
    sendMessage(msg) {
      if (!msg) {
        return;
      }
      this.pending = true;
      // eslint-disable-next-line
      docAsk(this.currentDoc._id, msg)
        .then((res) => {
          this.pending = false;
          if (res.data.code === 0) {
            this.currentAnswer = res.data.data.answer;
            this.currentQuestion = msg;
          } else {
            this.$message.error(res.data.message);
          }
        })
        .catch(() => {
          this.pending = false;
        });
      this.input = '';
    },
  },
  mounted() {
    this.fetchDocs();
  },
};
</script>

<style lang="scss" scoped>
.content {
  width: 400px;
  display: block;
  margin-left: 10px;
}

.display-area {
  margin-bottom: 10px;
  height: 300px;
  overflow: scroll;
}
</style>
