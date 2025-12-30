from flask import Blueprint, jsonify, request
from app.models.train_competition import Competition
from app.models.test_task import TestTask
from app.utils.jwt_utils import token_required

train_competition_bp = Blueprint('train_competition', __name__, url_prefix='/api/competition')


@train_competition_bp.route('/list', methods=['GET'])
@token_required
def get_competitions(current_user_id):
    """获取所有赛题列表"""
    try:
        competitions = Competition.get_all()
        return jsonify({
            'data': competitions
        }), 200
    except Exception as e:
        return jsonify({'error': f'获取赛题列表失败: {str(e)}'}), 500


@train_competition_bp.route('/select', methods=['POST'])
@token_required
def select_competition(current_user_id):
    """选择测试赛题"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据为空'}), 400
        
        training_id = data.get('training_id')
        competition_id = data.get('competition_id')
        
        if not training_id or not competition_id:
            return jsonify({'error': '训练ID和赛题ID不能为空'}), 400
        
        # 创建测试任务
        test_task = TestTask.create(training_id, competition_id)
        
        return jsonify({
            'message': '选择赛题成功',
            'data': test_task
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'选择赛题失败: {str(e)}'}), 500
