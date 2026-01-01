from app.database import get_db_cursor
from datetime import date

class TaskSubmit:
    @staticmethod
    def submit_task(user_id, status, created_time, name=None):
        """
        插入 render 表
        
        Args:
            user_id (int): 用户ID
            status (str): 渲染状态，必须是 'Rendering' 或 'Completed'
            render_cost (float): 渲染成本
            name (str, optional): 渲染任务名称
            
        Returns:
            int: 插入的 render_id
            
        Raises:
            ValueError: 如果 status 值无效
        """
        # 验证 status 值
        valid_statuses = ['Rendering', 'Completed']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")
        
        with get_db_cursor() as cursor:
            # 如果 name 为 None，则使用默认值
            if name is None:
                name = f"Render Task {date.today()}"
                
            try:
                # 插入数据
                created_time = "2026-01-06 00:00:00"
                print(f"Inserting task submit with name: {name}..., status: {status}, user_id: {user_id}, created_time: {created_time}")
                cursor.execute("""
                    INSERT INTO render (user_id, status, created_time, render_cost, name)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING render_id
                    """, (user_id, status, created_time, 0.0, name))
                
                # # 获取插入的 render_id
                # render_id = cursor.fetchone()[0]
                result = cursor.fetchone()
                if result:
                    render_id = result["render_id"]  # Correct way to access returned value
                else:
                    raise RuntimeError("Insert succeeded but no render_id returned")
                        
                
            except Exception as e:
                print(f"Error inserting task submit: {e}")
                raise    
            return render_id
        
    @staticmethod
    def insert(user_id: int, status: str, created_time: date, render_cost: float = None) -> int:
        """Insert a new render record"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO render 
                    (user_id, status, created_time, render_cost)
                    VALUES (%s, %s, %s, %s)
                    RETURNING render_id
                    """,
                    (user_id, status, created_time, render_cost)
                )
                result = cursor.fetchone()
                return result['render_id'] if result else None
        except Exception as e:
            print(f"Insert failed: {e}")
            raise e
    
    def set_completed(render_id: int) -> None:
        """Set the status of a render record to 'Completed'"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE render
                    SET status = 'Completed'
                    WHERE render_id = %s
                    """,
                    (render_id,)
                )
        except Exception as e:
            print(f"Update failed: {e}")

    def update_cost(render_id: int, render_cost: float):
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE render
                    SET render_cost = %s
                    WHERE render_id = %s
                    """,
                    (render_cost, render_id,)
                )
        except Exception as e:
            print(f"Update failed: {e}")
