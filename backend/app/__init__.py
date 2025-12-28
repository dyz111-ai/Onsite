# Flask 应用初始化
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from app.config import Config

# 创建应用实例
app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# 导出供其他模块使用
__all__ = ['app', 'socketio']
