from app.database import get_db_cursor


class Competition:
    def __init__(self, competition_id, created_time, end_time, status, type, number):
        self.competition_id = competition_id
        self.created_time = created_time
        self.end_time = end_time
        self.status = status
        self.type = type
        self.number = number
    
    @staticmethod
    def get_all():
        """获取所有赛题"""
        try:
            with get_db_cursor(commit=False) as cursor:
                cursor.execute(
                    """
                    SELECT competition_id, created_time, end_time, status, type, number
                    FROM competition
                    ORDER BY competition_id DESC
                    """
                )
                rows = cursor.fetchall()
                
                return [
                    {
                        'competition_id': row['competition_id'],
                        'created_time': row['created_time'].isoformat() if row['created_time'] else None,
                        'end_time': row['end_time'].isoformat() if row['end_time'] else None,
                        'status': row['status'],
                        'type': row['type'],
                        'number': row['number']
                    }
                    for row in rows
                ]
        except Exception as e:
            print(f"获取赛题列表失败: {e}")
            return []
