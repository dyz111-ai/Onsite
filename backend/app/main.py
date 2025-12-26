from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import subprocess
import os
import csv
import json
import threading
import platform

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def root():
    return {"message": "比赛平台API"}

import platform

def run_training_script(script_path):
    """在后台线程中执行训练脚本并实时发送输出"""
    try:
        socketio.emit('training_log', {'message': f'开始执行脚本: {os.path.basename(script_path)}'})

        # 根据操作系统选择执行方式
        if platform.system() == 'Windows':
            # Windows系统执行bat
            process = subprocess.Popen(
                ["cmd.exe", "/c", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=os.path.dirname(script_path),
                bufsize=1,
                universal_newlines=False
            )
        else:
            # Linux/Unix系统执行sh
            process = subprocess.Popen(
                ["bash", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=os.path.dirname(script_path),
                bufsize=1,
                universal_newlines=False
            )

        # 实时读取输出，尝试多种编码
        while True:
            line = process.stdout.readline()
            if not line:
                break
                
            try:
                # 尝试UTF-8解码
                decoded_line = line.decode('utf-8').strip()
            except UnicodeDecodeError:
                try:
                    # 如果UTF-8失败，尝试GBK
                    decoded_line = line.decode('gbk').strip()
                except UnicodeDecodeError:
                    # 如果都失败，忽略错误
                    decoded_line = line.decode('utf-8', errors='ignore').strip()

            if decoded_line:
                socketio.emit('training_log', {'message': decoded_line})

        # 等待进程结束
        returncode = process.wait()

        socketio.emit('training_log', {'message': f'脚本执行完毕，返回码: {returncode}'})

        if returncode == 0:
            socketio.emit('training_complete', {'status': 'success', 'message': '训练完成'})
        else:
            socketio.emit('training_complete', {'status': 'error', 'message': f'训练失败 (返回码: {returncode})'})

    except Exception as e:
        socketio.emit('training_log', {'message': f'执行脚本时发生异常: {str(e)}'})
        socketio.emit('training_complete', {'status': 'error', 'message': str(e)})

@app.route('/api/training/start', methods=['POST'])
def start_training():
    """触发训练脚本"""
    try:
        command_dir = os.path.join(os.path.dirname(__file__), '..', 'command')
        
        # 根据操作系统选择脚本文件
        if platform.system() == 'Windows':
            script_path = os.path.join(command_dir, 'run_autodl.bat')
        else:
            script_path = os.path.join(command_dir, 'run_autodl.sh')
        
        if not os.path.exists(script_path):
            return jsonify({"error": f"脚本文件不存在: {script_path}"}), 404
        
        # 在后台线程中执行
        thread = threading.Thread(target=run_training_script, args=(script_path,))
        thread.daemon = True
        thread.start()
        
        return jsonify({"message": "训练已启动", "status": "started"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/training/result', methods=['GET'])
def get_training_result():
    """获取训练结果CSV数据"""
    try:
        csv_path = r'D:\autodl_results\train\resource_usage.csv'

        if not os.path.exists(csv_path):
            return jsonify({"error": "CSV文件不存在"}), 404

        data = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)

        return jsonify({"data": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/task-submit/list', methods=['GET'])
def get_task_list():
    """获取任务列表"""
    try:
        # 确保 data 目录存在
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        json_path = os.path.join(data_dir, 'tasks.json')
        
        if not os.path.exists(json_path):
            return jsonify({"data": []}), 200
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify({"data": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/task-submit/create', methods=['POST'])
def create_task():
    """创建新任务"""
    try:
        task_data = request.get_json()
        
        if not task_data:
            return jsonify({"error": "请求数据为空"}), 400
        
        # 确保 data 目录存在
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        json_path = os.path.join(data_dir, 'tasks.json')
        
        # 读取现有任务列表
        task_list = []
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                task_list = json.load(f)
        
        # 添加新任务到列表开头
        task_list.insert(0, task_data)
        
        # 保存到 JSON 文件
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(task_list, f, ensure_ascii=False, indent=2)
        
        return jsonify({"message": "任务创建成功", "data": task_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/training/records', methods=['GET'])
def get_training_records():
    """获取训练记录列表"""
    try:
        # 确保 data 目录存在
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        json_path = os.path.join(data_dir, 'training_records.json')
        
        if not os.path.exists(json_path):
            return jsonify({"data": []}), 200
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify({"data": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/training/records', methods=['POST'])
def create_training_record():
    """创建新训练记录"""
    try:
        record_data = request.get_json()
        
        if not record_data:
            return jsonify({"error": "请求数据为空"}), 400
        
        # 确保 data 目录存在
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        json_path = os.path.join(data_dir, 'training_records.json')
        
        # 读取现有记录列表
        records_list = []
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                records_list = json.load(f)
        
        # 添加新记录到列表开头
        records_list.insert(0, record_data)
        
        # 保存到 JSON 文件
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(records_list, f, ensure_ascii=False, indent=2)
        
        return jsonify({"message": "训练记录创建成功", "data": record_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/training/records/<record_id>', methods=['PUT'])
def update_training_record(record_id):
    """更新训练记录（用于更新日志和结果）"""
    try:
        update_data = request.get_json()
        
        if not update_data:
            return jsonify({"error": "请求数据为空"}), 400
        
        # 确保 data 目录存在
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        json_path = os.path.join(data_dir, 'training_records.json')
        
        if not os.path.exists(json_path):
            return jsonify({"error": "训练记录文件不存在"}), 404
        
        # 读取现有记录列表
        with open(json_path, 'r', encoding='utf-8') as f:
            records_list = json.load(f)
        
        # 查找并更新记录
        found = False
        for i, record in enumerate(records_list):
            if record.get('id') == record_id:
                # 更新记录，保留原有字段，只更新提供的字段
                records_list[i].update(update_data)
                found = True
                break
        
        if not found:
            return jsonify({"error": "训练记录不存在"}), 404
        
        # 保存到 JSON 文件
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(records_list, f, ensure_ascii=False, indent=2)
        
        return jsonify({"message": "训练记录更新成功"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/training/records/<record_id>', methods=['DELETE'])
def delete_training_record(record_id):
    """删除训练记录"""
    try:
        # 确保 data 目录存在
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        json_path = os.path.join(data_dir, 'training_records.json')
        
        if not os.path.exists(json_path):
            return jsonify({"error": "训练记录文件不存在"}), 404
        
        # 读取现有记录列表
        with open(json_path, 'r', encoding='utf-8') as f:
            records_list = json.load(f)
        
        # 查找并删除记录
        original_length = len(records_list)
        records_list = [r for r in records_list if r.get('id') != record_id]
        
        if len(records_list) == original_length:
            return jsonify({"error": "训练记录不存在"}), 404
        
        # 保存到 JSON 文件
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(records_list, f, ensure_ascii=False, indent=2)
        
        return jsonify({"message": "训练记录删除成功"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/competition/list', methods=['GET'])
def get_competition_list():
    """获取赛题列表"""
    try:
        # 确保 data 目录存在
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        json_path = os.path.join(data_dir, 'competitions.json')
        
        if not os.path.exists(json_path):
            # 如果文件不存在，创建默认数据
            default_data = [{
                "id": "A卷1题",
                "download": "下载",
                "preview": "预览",
                "deadline": "2026.1.30",
                "status": "正常"
            }]
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=2)
            return jsonify({"data": default_data}), 200
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify({"data": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@socketio.on('connect')
def handle_connect():
    print('客户端已连接')

@socketio.on('disconnect')
def handle_disconnect():
    print('客户端已断开')

if __name__ == '__main__':
    socketio.run(app, debug=True, port=8000, allow_unsafe_werkzeug=True)

