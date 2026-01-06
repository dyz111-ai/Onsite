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

# Get Started
## frontend
### 1. 添加 NodeSource 源
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -

### 2. 安装 Node.js 22
sudo apt-get install -y nodejs

### 3. 验证安装
node -v
npm -v

### 4. 安装依赖包
npm install vite --save-dev

### 5. 运行
`npm run build`
并将生成的文件夹`frontend/dist`下的文件复制到`/frontend`下

## backend
### 建议conda装Python3.12
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
使用conda前source ~/miniconda3/etc/profile.d/conda.sh

### 安装 PostgreSQL 开发包
sudo apt-get update
sudo apt-get install libpq-dev python3-dev build-essential

### requirements.txt

pip install -r requirements.txt

## 部署
### nginx
`nano /etc/nginx/sites-available/vue-flask-app`并输入以下内容：
```
server {
    listen 80;
    server_name 106.15.38.222;  # 你的域名或服务器IP
    root /root/Onsite/frontend;  # Vue构建目录
    index index.html;

    # 前端静态文件
    location / {
        try_files $uri $uri/ /index.html;
        # 缓存静态资源
        location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # 反向代理到Flask后端
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 防止直接访问后端端口
    location = /health {
        deny all;
        return 404;
    }

    # 错误页面
    error_page 404 /index.html;
    error_page 500 502 503 504 /50x.html;
    
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
```
保存配置后，执行以下命令：
```
# 创建符号链接
ln -s /etc/nginx/sites-available/vue-flask-app /etc/nginx/sites-enabled/

# 测试Nginx配置
nginx -t

# 重启Nginx
systemctl restart nginx
```

# 当阿里云数据库服务器停止后重新启动
https://rdsnext.console.aliyun.com/rdsList/cn-shanghai
，点击对应实例那一行的“操作”那一列的“更多”——“启动实例”

# 当阿里云主服务器停止后重新启动
https://ecs.console.aliyun.com/server/i-uf6djyjo70lv38bcmqsp/detail?regionId=cn-shanghai&serverLiteToken=1767421711939&__refreshToken=1767421712273