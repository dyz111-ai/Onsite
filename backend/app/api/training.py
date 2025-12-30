# 训练相关的 API 路由
from flask import Blueprint, jsonify, request
import threading
import os
import csv
from app.models.training_task import TrainingTask
from app.utils.jwt_utils import decode_token
from app.services.training_service import TrainingService

training_bp = Blueprint('training', __name__, url_prefix='/api/training')


@training_bp.route('/start', methods=['POST'])
def start_training():
    """触发训练脚本"""
    try:
        from app import socketio
        
        data = request.get_json() or {}
        training_id = data.get('training_id')
        
        if not training_id:
            return jsonify({"error": "缺少 training_id 参数"}), 400
        
        script_path = TrainingService.get_script_path()
        
        if not os.path.exists(script_path):
            return jsonify({"error": f"脚本文件不存在: {script_path}"}), 404
        
        # 在后台线程中执行，传递 training_id
        thread = threading.Thread(
            target=TrainingService.run_training_script, 
            args=(script_path, training_id, socketio)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({"message": "训练已启动", "status": "started"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@training_bp.route('/records', methods=['GET'])
def get_training_records():
    """获取当前用户的训练记录列表"""
    try:
        # 从请求头获取 token 并验证
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Token 格式错误'}), 401
        
        if not token:
            return jsonify({'error': '缺少认证 token'}), 401
        
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Token 无效或已过期'}), 401
        
        user_id = payload['user_id']
        
        # 获取当前用户的训练记录
        records = TrainingTask.get_all_by_user(user_id)
        
        return jsonify({
            "data": [record.to_dict() for record in records]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@training_bp.route('/records/<int:training_id>', methods=['GET'])
def get_training_record(training_id):
    """获取单个训练记录"""
    try:
        record = TrainingTask.get_by_id(training_id)
        if not record:
            return jsonify({"error": "训练记录不存在"}), 404
        
        return jsonify({"data": record.to_dict()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@training_bp.route('/records', methods=['POST'])
def create_training_record():
    """创建训练记录（点击新增训练按钮）"""
    try:
        # 从请求头获取 token 并验证
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Token 格式错误'}), 401
        
        if not token:
            return jsonify({'error': '缺少认证 token'}), 401
        
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Token 无效或已过期'}), 401
        
        user_id = payload['user_id']
        
        # 创建训练记录，status='Training'，其他字段为 0
        record = TrainingTask.create(
            user_id=user_id,
            status='Training',
            train_cost=0.0,
            test_score=0.0,
            total_score=0.0
        )
        
        return jsonify({
            "message": "训练记录创建成功",
            "data": record.to_dict()
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@training_bp.route('/records/<int:training_id>', methods=['DELETE'])
def delete_training_record(training_id):
    """删除训练记录"""
    try:
        TrainingTask.delete(training_id)
        return jsonify({"message": "训练记录删除成功"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@training_bp.route('/records/<int:training_id>/status', methods=['PUT'])
def update_training_status(training_id):
    """更新训练状态"""
    try:
        import random
        from app.database import get_db_cursor
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据为空'}), 400
        
        status = data.get('status')
        test_score = data.get('test_score')
        total_score = data.get('total_score')
        
        if not status:
            return jsonify({'error': '状态不能为空'}), 400
        
        # 获取训练记录
        record = TrainingTask.get_by_id(training_id)
        if not record:
            return jsonify({'error': '训练记录不存在'}), 404
        
        # 更新状态
        record.status = status
        
        # 如果状态变为 Tested，自动计算分数
        if status == 'Tested':
            # 生成 0-1 之间的随机测试分数
            if test_score is None:
                test_score = round(random.uniform(0, 1), 4)
            
            # 获取渲染成本
            with get_db_cursor(commit=False) as cursor:
                cursor.execute(
                    """
                    SELECT COALESCE(SUM(r.render_cost), 0) as render_cost
                    FROM training_render_relation trr
                    LEFT JOIN render r ON trr.render_id = r.render_id
                    WHERE trr.training_id = %s
                    """,
                    (training_id,)
                )
                result = cursor.fetchone()
                render_cost = float(result['render_cost']) if result else 0.0
            
            # 计算总分：train_cost + test_score + render_cost
            total_score = round(record.train_cost + test_score + render_cost, 4)
            
            record.test_score = float(test_score)
            record.total_score = float(total_score)
        else:
            # 其他状态，如果提供了分数就更新
            if test_score is not None:
                record.test_score = float(test_score)
            if total_score is not None:
                record.total_score = float(total_score)
        
        record.update()
        
        return jsonify({
            "message": "状态更新成功",
            "data": record.to_dict()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@training_bp.route('/monitor/<int:training_id>', methods=['GET'])
def get_training_monitor(training_id):
    """获取训练监控数据"""
    try:
        # 构建 CSV 文件路径
        cache_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'cache', 'train')
        csv_path = os.path.join(cache_dir, f'train{training_id}', 'resource_usage.csv')
        
        if not os.path.exists(csv_path):
            return jsonify({"error": "监控数据文件不存在"}), 404
        
        # 读取 CSV 数据
        data = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        
        return jsonify({"data": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@training_bp.route('/logs/<int:training_id>', methods=['GET'])
def get_training_logs(training_id):
    """获取训练日志"""
    try:
        # 构建日志文件路径
        cache_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'cache', 'train')
        log_path = os.path.join(cache_dir, f'train{training_id}', 'train.log')
        
        if not os.path.exists(log_path):
            return jsonify({"error": "日志文件不存在"}), 404
        
        # 读取日志内容
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            log_content = f.read()
        
        return jsonify({"data": log_content}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
