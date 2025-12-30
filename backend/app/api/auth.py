from flask import Blueprint, request, jsonify
from app.models.user import User
from app.models.admin import Admin
from app.utils.jwt_utils import create_token, token_required

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def validate_password(password):
    """验证密码强度（至少6位）"""
    return len(password) >= 6

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据为空'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # 验证必填字段
        if not username or not password:
            return jsonify({'error': '用户名和密码不能为空'}), 400
        
        # 验证用户名长度
        if len(username) < 3 or len(username) > 20:
            return jsonify({'error': '用户名长度必须在3-20个字符之间'}), 400
        
        # 验证密码强度
        if not validate_password(password):
            return jsonify({'error': '密码长度至少为6位'}), 400
        
        # 创建用户
        try:
            user = User.create_user(username, password)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
        # 生成 token
        token = create_token(user.id)
        
        return jsonify({
            'message': '注册成功',
            'token': token,
            'user': user.to_public_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'注册失败: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据为空'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # 验证必填字段
        if not username or not password:
            return jsonify({'error': '用户名和密码不能为空'}), 400
        
        # 查找用户
        user = User.find_by_username(username)
        if not user:
            return jsonify({'error': '用户名或密码错误'}), 401
        
        # 验证密码
        if not user.check_password(password):
            return jsonify({'error': '用户名或密码错误'}), 401
        
        # 生成 token
        token = create_token(user.id)
        
        return jsonify({
            'message': '登录成功',
            'token': token,
            'user': user.to_public_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'登录失败: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user_id):
    """获取当前登录用户信息"""
    try:
        user = User.find_by_id(current_user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        return jsonify({
            'user': user.to_public_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取用户信息失败: {str(e)}'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password(current_user_id):
    """修改密码"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据为空'}), 400
        
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')
        
        # 验证必填字段
        if not old_password or not new_password:
            return jsonify({'error': '旧密码和新密码不能为空'}), 400
        
        # 验证新密码强度
        if not validate_password(new_password):
            return jsonify({'error': '新密码长度至少为6位'}), 400
        
        # 查找用户
        user = User.find_by_id(current_user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 验证旧密码
        if not user.check_password(old_password):
            return jsonify({'error': '旧密码错误'}), 401
        
        # 更新密码
        from werkzeug.security import generate_password_hash
        user.password_hash = generate_password_hash(new_password)
        user.save()
        
        return jsonify({
            'message': '密码修改成功'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'修改密码失败: {str(e)}'}), 500

@auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    """管理员登录"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据为空'}), 400
        
        account = data.get('account', '').strip()
        password = data.get('password', '')
        
        # 验证必填字段
        if not account or not password:
            return jsonify({'error': '账号和密码不能为空'}), 400
        
        # 查找管理员
        admin = Admin.get_by_account(account)
        if not admin:
            return jsonify({'error': '账号或密码错误'}), 401
        
        # 验证密码
        if not admin.verify_password(password):
            return jsonify({'error': '账号或密码错误'}), 401
        
        # 生成 token，包含角色信息
        token = create_token(admin.admin_id, role='admin')
        
        return jsonify({
            'message': '登录成功',
            'token': token,
            'admin': {
                'admin_id': admin.admin_id,
                'account': admin.account,
                'role': 'admin'
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'登录失败: {str(e)}'}), 500
