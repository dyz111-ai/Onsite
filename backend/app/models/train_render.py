from app.database import get_db_cursor


class Render:
    def __init__(self, render_id, user_id, name, status, created_time, render_cost):
        self.render_id = render_id
        self.user_id = user_id
        self.name = name
        self.status = status
        self.created_time = created_time
        self.render_cost = render_cost
    
    def to_dict(self):
        """转换为字典"""
        return {
            'render_id': self.render_id,
            'user_id': self.user_id,
            'name': self.name,
            'status': self.status,
            'created_time': str(self.created_time) if self.created_time else None,
            'render_cost': self.render_cost
        }
    
    @staticmethod
    def get_all_by_user(user_id):
        """获取指定用户的所有渲染记录"""
        try:
            with get_db_cursor(commit=False) as cursor:
                cursor.execute(
                    """
                    SELECT render_id, user_id, name, status, created_time, render_cost
                    FROM render
                    WHERE user_id = %s
                    ORDER BY created_time DESC
                    """,
                    (user_id,)
                )
                results = cursor.fetchall()
                
                return [Render(
                    render_id=row['render_id'],
                    user_id=row['user_id'],
                    name=row.get('name', ''),
                    status=row['status'],
                    created_time=row['created_time'],
                    render_cost=row['render_cost']
                ) for row in results]
        except Exception as e:
            print(f"获取渲染记录失败: {e}")
            return []
    
    @staticmethod
    def get_by_training_id(training_id):
        """获取指定训练关联的所有渲染记录"""
        try:
            with get_db_cursor(commit=False) as cursor:
                cursor.execute(
                    """
                    SELECT r.render_id, r.user_id, r.name, r.status, r.created_time, r.render_cost
                    FROM render r
                    INNER JOIN training_render_relation trr ON r.render_id = trr.render_id
                    WHERE trr.training_id = %s
                    ORDER BY r.created_time DESC
                    """,
                    (training_id,)
                )
                results = cursor.fetchall()
                
                return [Render(
                    render_id=row['render_id'],
                    user_id=row['user_id'],
                    name=row.get('name', ''),
                    status=row['status'],
                    created_time=row['created_time'],
                    render_cost=row['render_cost']
                ) for row in results]
        except Exception as e:
            print(f"获取训练关联的渲染记录失败: {e}")
            return []


class TrainingRenderRelation:
    @staticmethod
    def create_relations(training_id, render_ids):
        """创建训练和渲染的关联关系"""
        try:
            with get_db_cursor() as cursor:
                # 先删除该训练的所有旧关联
                cursor.execute(
                    "DELETE FROM training_render_relation WHERE training_id = %s",
                    (training_id,)
                )
                
                # 插入新关联
                for render_id in render_ids:
                    cursor.execute(
                        """
                        INSERT INTO training_render_relation (training_id, render_id)
                        VALUES (%s, %s)
                        """,
                        (training_id, render_id)
                    )
                
                return True
        except Exception as e:
            print(f"创建训练渲染关联失败: {e}")
            raise e
    
    @staticmethod
    def get_render_ids_by_training(training_id):
        """获取训练关联的所有渲染ID"""
        try:
            with get_db_cursor(commit=False) as cursor:
                cursor.execute(
                    "SELECT render_id FROM training_render_relation WHERE training_id = %s",
                    (training_id,)
                )
                results = cursor.fetchall()
                return [row['render_id'] for row in results]
        except Exception as e:
            print(f"获取训练关联的渲染ID失败: {e}")
            return []
