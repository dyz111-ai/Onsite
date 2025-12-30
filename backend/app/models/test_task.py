from app.database import get_db_cursor


class TestTask:
    def __init__(self, training_id, competition_id, score=None):
        self.training_id = training_id
        self.competition_id = competition_id
        self.score = score
    
    @staticmethod
    def create(training_id, competition_id):
        """创建测试任务"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO test_task (training_id, competition_id, score)
                    VALUES (%s, %s, %s)
                    RETURNING training_id, competition_id, score
                    """,
                    (training_id, competition_id, 0.0)
                )
                row = cursor.fetchone()
                
                return {
                    'training_id': row['training_id'],
                    'competition_id': row['competition_id'],
                    'score': row['score']
                }
        except Exception as e:
            print(f"创建测试任务失败: {e}")
            raise e
    
    @staticmethod
    def get_by_training_id(training_id):
        """根据训练ID获取测试任务"""
        try:
            with get_db_cursor(commit=False) as cursor:
                cursor.execute(
                    """
                    SELECT training_id, competition_id, score
                    FROM test_task
                    WHERE training_id = %s
                    """,
                    (training_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return {
                        'training_id': row['training_id'],
                        'competition_id': row['competition_id'],
                        'score': row['score']
                    }
                return None
        except Exception as e:
            print(f"获取测试任务失败: {e}")
            return None
