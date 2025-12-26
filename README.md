# 比赛平台

一个基于 Vue 3 和 Flask 的比赛平台项目。

## 项目结构

```
competition-platform/
├── frontend/          # Vue 3 前端
└── backend/           # Flask 后端
```

## 快速开始

### 后端启动

```bash
cd backend
pip install -r requirements.txt
python -m app.main
```

或者：
```bash
cd backend
pip install -r requirements.txt
flask --app app.main run --port 8000 --debug
```

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

前端访问地址：http://localhost:3000
后端API地址：http://localhost:8000

## 功能说明

- 选手提交比赛数据
- 数据传递到远程服务器处理（待实现）
- 模型训练和评估（待实现）
- 结果展示

## 待实现

- 远程服务器数据处理接口
- 模型训练和评估逻辑
- 数据库持久化
- 用户认证系统
