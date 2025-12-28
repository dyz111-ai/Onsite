import psycopg2
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import get_db_cursor

class User:
    def __init__(self, participant_id, account, password_hash):
        self.id = participant_id
        self.username = account
        self.password_hash = password_hash
    
    def to_public_dict(self):
        """转换为公开字典（不包含密码）"""
        return {
            'id': self.id,
            'username': self.username
        }
    
    @staticmethod
    def find_by_username(username):
        """根据用户名查找用户"""
        try:
            with get_db_cursor(commit=False) as cursor:
                cursor.execute(
                    "SELECT participant_id, account, password FROM participant WHERE account = %s",
                    (username,)
                )
                result = cursor.fetchone()
                
                if result:
                    return User(
                        participant_id=result['participant_id'],
                        account=result['account'],
                        password_hash=result['password']
                    )
                return None
        except Exception as e:
            print(f"查找用户失败: {e}")
            return None
    
    @staticmethod
    def find_by_id(user_id):
        """根据ID查找用户"""
        try:
            with get_db_cursor(commit=False) as cursor:
                cursor.execute(
                    "SELECT participant_id, account, password FROM participant WHERE participant_id = %s",
                    (user_id,)
                )
                result = cursor.fetchone()
                
                if result:
                    return User(
                        participant_id=result['participant_id'],
                        account=result['account'],
                        password_hash=result['password']
                    )
                return None
        except Exception as e:
            print(f"查找用户失败: {e}")
            return None
    
    def save(self):
        """保存用户（插入或更新）"""
        try:
            with get_db_cursor() as cursor:
                # 检查用户是否已存在
                cursor.execute(
                    "SELECT participant_id FROM participant WHERE participant_id = %s",
                    (self.id,)
                )
                exists = cursor.fetchone()
                
                if exists:
                    # 更新用户
                    cursor.execute(
                        "UPDATE participant SET account = %s, password = %s WHERE participant_id = %s",
                        (self.username, self.password_hash, self.id)
                    )
                else:
                    # 插入新用户
                    cursor.execute(
                        "INSERT INTO participant (participant_id, account, password) VALUES (%s, %s, %s)",
                        (self.id, self.username, self.password_hash)
                    )
        except Exception as e:
            print(f"保存用户失败: {e}")
            raise e
    
    @staticmethod
    def create_user(username, password):
        """创建新用户"""
        # 检查用户名是否已存在
        if User.find_by_username(username):
            raise ValueError('用户名已存在')
        
        # 生成新的 participant_id
        try:
            with get_db_cursor() as cursor:
                # 获取当前最大的 participant_id
                cursor.execute("SELECT COALESCE(MAX(participant_id), 0) + 1 as next_id FROM participant")
                result = cursor.fetchone()
                next_id = result['next_id']
                
                # 创建用户
                password_hash = generate_password_hash(password)
                user = User(participant_id=next_id, account=username, password_hash=password_hash)
                user.save()
                return user
        except Exception as e:
            print(f"创建用户失败: {e}")
            raise e
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

