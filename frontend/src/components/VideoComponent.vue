<template>
  <div class="video-component">
    <div v-if="loading" class="loading">
      <p>加载中...</p>
    </div>
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
    </div>
    <div v-else-if="videoSrc" class="video-container">
      <video 
        :src="videoSrc" 
        controls 
        preload="metadata"
        @loadeddata="onVideoLoaded"
        @error="onVideoError"
        class="video-player"
      >
        您的浏览器不支持视频播放。
      </video>
    </div>
    <div v-else class="no-video">
      <p>没有找到视频文件</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'VideoComponent',
  props: {
    // 任务ID，用于构建视频路径
    taskId: {
      type: String,
      required: true
    },
    // 任务类型，默认为competition
    taskType: {
      type: String,
      default: 'competition'
    }
  },
  data() {
    return {
      videoSrc: null,
      loading: false,
      error: null,
      videoDuration: null
    }
  },
  watch: {
    taskId: {
      immediate: true,
      handler(newId) {
        if (newId) {
          this.loadVideo()
        }
      }
    }
  },
  methods: {
    async loadVideo() {
      this.loading = true
      this.error = null
      this.videoSrc = null

      try {
        // 构建视频文件路径
        const videoPath = `/cache/${this.taskType}/video/${this.taskId}.mp4`
        
        // 检查视频是否存在
        const response = await fetch(videoPath, { method: 'HEAD' })
        
        if (response.ok) {
          // 设置视频源
          this.videoSrc = videoPath
        } else {
          this.error = `视频文件不存在: ${videoPath}`
        }
      } catch (err) {
        this.error = `加载视频时出错: ${err.message}`
      } finally {
        this.loading = false
      }
    },
    onVideoLoaded() {
      // 视频加载完成后的处理
      console.log('视频加载完成')
    },
    onVideoError() {
      // 视频加载失败的处理
      this.error = '视频加载失败'
    }
  },
  mounted() {
    // 组件挂载时加载视频
    this.loadVideo()
  }
}
</script>

<style scoped>
.video-component {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

.video-container {
  width: 100%;
  text-align: center;
}

.video-player {
  width: 100%;
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.loading, .error, .no-video {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
  text-align: center;
  color: #666;
}

.error {
  color: #e74c3c;
}
</style>