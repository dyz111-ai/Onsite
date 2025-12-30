# 渲染相关的 API 路由
from flask import Blueprint, jsonify, request
from app.models.train_render import Render, TrainingRenderRelation
from app.utils.jwt_utils import decode_token

render_bp = Blueprint('render', __name__, url_prefix='/api/render')


@render_bp.route('/records', methods=['GET'])
def get_render_records():
    """获取当前用户的渲染记录列表"""
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
        
        # 获取当前用户的渲染记录
        records = Render.get_all_by_user(user_id)
        
        return jsonify({
            "data": [record.to_dict() for record in records]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@render_bp.route('/training/<int:training_id>', methods=['GET'])
def get_training_renders(training_id):
    """获取指定训练关联的渲染记录"""
    try:
        records = Render.get_by_training_id(training_id)
        
        return jsonify({
            "data": [record.to_dict() for record in records]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@render_bp.route('/training/<int:training_id>/relation', methods=['POST'])
def create_training_render_relation(training_id):
    """创建训练和渲染的关联关系"""
    try:
        data = request.get_json() or {}
        render_ids = data.get('render_ids', [])
        
        if not isinstance(render_ids, list):
            return jsonify({"error": "render_ids 必须是数组"}), 400
        
        TrainingRenderRelation.create_relations(training_id, render_ids)
        
        return jsonify({
            "message": "关联创建成功",
            "training_id": training_id,
            "render_ids": render_ids
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
