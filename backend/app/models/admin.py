from app.database import get_db_cursor
import bcrypt


class Admin:
    def __init__(self, admin_id, account, password):
        self.admin_id = admin_id
        self.account = account
        self.password = password
    
    @staticmethod
    def get_by_account(account):
        """根据账号获取管理员"""
        try:
            with get_db_cursor(commit=False) as cursor:
                cursor.execute(
                    "SELECT admin_id, account, password FROM admin WHERE account = %s",
                    (account,)
                )
                row = cursor.fetchone()
                
                if row:
                    return Admin(
                        admin_id=row['admin_id'],
                        account=row['account'],
                        password=row['password']
                    )
                return None
        except Exception as e:
            print(f"获取管理员失败: {e}")
            return None
    
    def verify_password(self, password):
        """验证密码"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
        except:
            # 如果密码不是 bcrypt 加密的，直接比较
            return self.password == password
    
    @staticmethod
    def create(account, password):
        """创建管理员"""
        try:
            # 加密密码
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO admin (account, password)
                    VALUES (%s, %s)
                    RETURNING admin_id, account, password
                    """,
                    (account, hashed.decode('utf-8'))
                )
                row = cursor.fetchone()
                
                return Admin(
                    admin_id=row['admin_id'],
                    account=row['account'],
                    password=row['password']
                )
        except Exception as e:
            print(f"创建管理员失败: {e}")
            raise e
