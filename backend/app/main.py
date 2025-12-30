from flask import jsonify
from app import app, socketio

# 注册蓝图
from app.api.auth import auth_bp
from app.api.training import training_bp
from app.api.train_render import render_bp
from app.api.train_competition import competition_bp

app.register_blueprint(auth_bp)
app.register_blueprint(training_bp)
app.register_blueprint(render_bp)
app.register_blueprint(competition_bp)


@app.route('/')
def root():
    return {"message": "比赛平台API"}


@socketio.on('connect')
def handle_connect():
    print('客户端已连接')


@socketio.on('disconnect')
def handle_disconnect():
    print('客户端已断开')


if __name__ == '__main__':
    socketio.run(app, debug=True, port=8000, allow_unsafe_werkzeug=True)
