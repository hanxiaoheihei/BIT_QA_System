  <template>
  <el-card class="container">
    <div slot="header">
      <span class="title">💡BIT Open QA</span>
      <el-button
        type="text"
        @click="showTips = !showTips"
        style="float: right; padding: 5px 0;"
        >我都会什么？</el-button
      >
    </div>
    <el-collapse-transition>
      <div class="tip-layer" v-show="showTips">
        <el-tabs tab-position="bottom" style="margin-bottom: 4px;">
          <el-tab-pane v-for="(tip, idx) in tips" :key="idx" :label="tip.title">
            <p class="tip-title">{{ tip.title }}</p>
            <span>{{ tip.desc }}</span>
            <el-button
              class="btn-try"
              type="primary"
              size="small"
              @click="sendMessage(getMsg(tip.message))"
              :loading="pending"
              >体验一下</el-button
            >
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-collapse-transition>
    <div class="messages" v-chat-scroll="{ always: true, smooth: true }">
      <div
        v-for="(message, index) in messages"
        :key="index"
        class="chatbox"
        :class="'user' + message.user"
      >
        {{ message.content }}
      </div>
    </div>
    <el-input
      v-model="input"
      placeholder="请输入内容"
      @keyup.enter.native="!pending && sendMessage(input)"
    >
      <template slot="append">
        <el-button @click="sendMessage(input)" :loading="pending"
          >发送</el-button
        >
      </template>
    </el-input>
  </el-card>
</template>

<script>
import { sendMessage } from '@/api';

export default {
  name: 'home',
  data() {
    return {
      messages: [{ user: 1, content: 'Hello，我是智能问答机器人~' }],
      input: '',
      senderId: 
        new Date().toISOString()
        + Math.random()
          .toString(36)
          .substr(2)
          .toUpperCase(),
      showTips: false,
      pending: false,
      tips: [
        // {
        //   title: '深度语义匹配',
        //   desc: '基于深度语义匹配技术，构建 FAQ 单轮问答。',
        //   message: '我忘记开发票了，可以补吗?',
        // },
        // {
        //   title: '多轮问答场景',
        //   desc: '对于复杂高频的问答场景，梳理业务逻辑，构建多轮问答。',
        //   message: '平台可以用微信支付吗?',
        // },
        // {
        //   title: '上传立刻提问',
        //   desc: '对于规章制度等文件，无需抽取 QA 对，基于机器阅读技术，实现上传立即提问。',
        //   message: '你们的滑轮多少钱?',
        // },
        {
          title: '开放领域问答',
          desc: '基于机器阅读与爬虫技术，答你所问，告别百度。',
          message: '洛杉矶和中国哪个城市纬度一样?',
        },
        {
          title: '通用机器人技能',
          desc: '查百科，查邮编，查天气，说笑话，讲段子...应有尽有。',
          message: ['北京理工大学的百度百科', '北京今天的天气', '北京的邮编'],
        },
      ],
    };
  },
  components: {},
  methods: {
    sendMessage(msg) {
      if (!msg) {
        return;
      }
      this.pending = true;
      this.messages.push({
        user: 0,
        content: msg,
      });
      sendMessage(this.senderId, msg)
        .then((res) => {
          console.log(res.data.results)
          this.messages.push({
              user: 1,
              content:res.data.results[0].answer,
            });
          
          this.pending = false;
        })
        .catch(() => {
          this.pending = false;
        });
      this.input = '';
    },
    getMsg(msg) {
      if (Array.isArray(msg)) {
        return msg[Math.floor(Math.random() * msg.length)];
      }
      return msg;
    },
  },
};
</script>

<style lang="scss" scoped>
.messages {
  overflow: scroll;
  margin-bottom: 20px;
  flex: 1;
  .chatbox {
    &.user0 {
      float: right;
    }
    &.user1 {
      float: left;
    }
    padding: 5px 15px 6px;
    max-width: 300px;
    border: 1px solid #2d8cf0;
    border-radius: 4px;
    clear: both;
    color: #2d8cf0;
    font-size: 13px;
    margin: 2px 0;
  }
}

.tip-layer {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  padding: 0 20px;
  box-sizing: border-box;
  background: rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(5px);
  .tip-title {
    font-weight: bold;
  }
  .btn-try {
    position: absolute;
    top: 10px;
    right: 0;
  }
}
</style>
