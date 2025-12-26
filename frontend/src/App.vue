<template>
  <div id="app">
    <nav class="sidebar">
      <div class="logo">Onsite测训一体</div>
      <ul class="nav-menu">
        <li>
          <router-link to="/competition" class="nav-item">赛题查看</router-link>
        </li>
        <li>
          <router-link to="/task-submit" class="nav-item">场景提交</router-link>
        </li>
        <li>
          <router-link to="/training" class="nav-item">训练提交</router-link>
        </li>
        <li>
          <router-link to="/monitor" class="nav-item">监控面板</router-link>
        </li>
        <li>
          <router-link to="/evaluation" class="nav-item">测试评估</router-link>
        </li>
        <li>
          <router-link to="/result" class="nav-item">结果展示</router-link>
        </li>
      </ul>
    </nav>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: Arial, sans-serif;
  min-height: 100vh;
  display: flex;
  background: #f5f5f5;
}

.sidebar {
  width: 200px;
  background: #2c3e50;
  color: white;
  min-height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
}

.logo {
  padding: 2rem 1rem;
  font-size: 1.2rem;
  font-weight: bold;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.nav-menu {
  list-style: none;
  padding: 1rem 0;
}

.nav-menu li {
  margin: 0;
}

.nav-item {
  display: block;
  padding: 1rem 1.5rem;
  color: #ecf0f1;
  text-decoration: none;
  transition: background 0.3s;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.nav-item.router-link-active {
  background: #42b983;
  border-left: 4px solid #fff;
}

.main-content {
  margin-left: 200px;
  padding: 0;
  flex: 1;
  min-height: 100vh;
  width: calc(100% - 200px);
  max-width: 100%;
  box-sizing: border-box;
}
</style>
