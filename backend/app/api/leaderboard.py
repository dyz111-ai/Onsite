from flask import Blueprint, request, jsonify
from app.models.training_task import TrainingTask
from app.utils.jwt_utils import token_required

leaderboard_bp = Blueprint('leaderboard', __name__, url_prefix='/api/leaderboard')

@leaderboard_bp.route('/list', methods=['GET'])
@token_required
def get_leaderboard(current_user_id):
    """
    获取总分排行榜数据
    权限：需要登录
    """
    try:
        # 获取总分排行榜数据
        leaderboard_data = TrainingTask.get_leaderboard()
        
        # 格式化响应数据
        formatted_data = []
        for item in leaderboard_data:
            formatted_data.append({
                'rank': item['global_rank'],
                'user_id': item['user_id'],
                'account': item['account'],
                'score': float(item['max_score']),
                'created_time': item['created_time'].strftime('%Y-%m-%d %H:%M:%S') if item['created_time'] else None
            })
        
        return jsonify({
            'message': '获取总分排行榜成功',
            'data': formatted_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取总分排行榜失败: {str(e)}'}), 500

@leaderboard_bp.route('/cost', methods=['GET'])
@token_required
def get_cost_leaderboard(current_user_id):
    """
    获取训练成本排行榜数据
    权限：需要登录
    """
    try:
        # 获取成本排行榜数据
        leaderboard_data = TrainingTask.get_leaderboard_by_cost()
        
        # 格式化响应数据
        formatted_data = []
        for item in leaderboard_data:
            formatted_data.append({
                'rank': item['global_rank'],
                'user_id': item['user_id'],
                'account': item['account'],
                'cost': item['min_cost'] if item['min_cost'] == '无穷大' else float(item['min_cost']),
                'created_time': item['created_time'].strftime('%Y-%m-%d %H:%M:%S') if item['created_time'] else None
            })
        
        return jsonify({
            'message': '获取成本排行榜成功',
            'data': formatted_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取成本排行榜失败: {str(e)}'}), 500

@leaderboard_bp.route('/test_score', methods=['GET'])
@token_required
def get_test_score_leaderboard(current_user_id):
    """
    获取测试分数排行榜数据
    权限：需要登录
    """
    try:
        # 获取测试分数排行榜数据
        leaderboard_data = TrainingTask.get_leaderboard_by_test_score()
        
        # 格式化响应数据
        formatted_data = []
        for item in leaderboard_data:
            formatted_data.append({
                'rank': item['global_rank'],
                'user_id': item['user_id'],
                'account': item['account'],
                'test_score': float(item['max_test_score']),
                'created_time': item['created_time'].strftime('%Y-%m-%d %H:%M:%S') if item['created_time'] else None
            })
        
        return jsonify({
            'message': '获取测试分数排行榜成功',
            'data': formatted_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取测试分数排行榜失败: {str(e)}'}), 500

@leaderboard_bp.route('/user/best', methods=['GET'])
@token_required
def get_user_best_score(current_user_id):
    """
    获取当前用户的最佳成绩
    权限：需要登录
    """
    try:
        # 获取用户最佳成绩
        best_task = TrainingTask.get_user_best_score(current_user_id)
        
        if not best_task:
            return jsonify({
                'message': '用户暂无训练记录',
                'data': None
            }), 200
        
        return jsonify({
            'message': '获取用户最佳成绩成功',
            'data': {
                'user_id': best_task.user_id,
                'score': float(best_task.total_score) if best_task.total_score else 0.0,
                'created_time': best_task.created_time.strftime('%Y-%m-%d %H:%M:%S') if best_task.created_time else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取用户最佳成绩失败: {str(e)}'}), 500