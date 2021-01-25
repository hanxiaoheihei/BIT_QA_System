<template>
  <div id="app">
    <div id="nav">
      <router-link to="/">主页</router-link> |
<!--      <router-link to="/faqs">FAQ Data</router-link> |-->
      <router-link to="/docs">阅读理解</router-link> |
      <router-link to="/Sort">理解可视化</router-link> |
      <router-link to="/Sort2">推理可视化</router-link>
    </div>
    <el-button
      icon="el-icon-menu"
      circle
      class="mobile-nav-btn"
      @click="drawer = !drawer"
      size="small"
    ></el-button>
    <el-drawer :visible.sync="drawer" direction="ltr" :show-close="false">
      <el-menu router @select="drawer = false">
        <el-menu-item index="/"> Home </el-menu-item>
<!--        <el-menu-item index="/faqs"> FAQ Data </el-menu-item>-->
        <el-menu-item index="/docs"> Documents </el-menu-item>
      </el-menu>
    </el-drawer>

    <transition name="fade-transform" mode="out-in">
      <router-view />
    </transition>
  </div>
</template>

<script>
export default {
  name: 'app',
  components: {},
  data() {
    return {
      drawer: false,
    };
  },
};
</script>

<style lang="scss">
#app {
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB",
    "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin-top: 60px;
  #nav {
    text-align: center;
    a:link,
    :visited {
      color: #333333;
    }
    a:hover {
      color: #666666;
    }
  }
  .mobile-nav-btn {
    display: none;
  }
}

body {
  background: #f2f6fc;
}

/*fade-transform*/
.fade-transform-leave-active,
.fade-transform-enter-active {
  transition: all 0.5s;
}
.fade-transform-enter {
  opacity: 0;
  transform: translateX(-30px);
}
.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.container {
  margin: 40px auto;
  width: 800px;
  height: 600px;
  position: relative;
  display: flex;
  flex-direction: column;
  .title {
    font-weight: bold;
  }
}

.mobile-nav-btn {
  display: none;
}

.el-card__body {
  display: flex;
  flex-direction: column;
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  top: 63px;
}

@media screen and (max-width: 768px) {
  .container {
    margin: 0;
    box-shadow: none !important;
    border: 0 !important;
    .title {
      font-weight: bold;
      margin-left: 30px;
    }
  }

  #app {
    #nav {
      display: none;
    }
    .mobile-nav-btn {
      display: block;
      position: absolute;
      top: 16px;
      left: 12px;
      z-index: 10;
    }
  }
  body,
  html,
  .container,
  #app {
    margin: 0;
    height: 100%;
    width: 100%;
  }

  /*fade-transform*/
  .fade-transform-leave-active,
  .fade-transform-enter-active {
    transition: none;
  }
  .fade-transform-enter,
  .fade-transform-leave-to {
    opacity: 1;
    transform: none;
  }

  .el-dialog {
    width: 100vw !important;
  }
}
</style>
