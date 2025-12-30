from app.database import get_db_cursor
from datetime import date

class Competition:
    @staticmethod
    def get_all():
        """Get all competitions"""
        try:
            with get_db_cursor(commit=False) as cursor:
                cursor.execute(
                    "SELECT competition_id, created_time, end_time, status, type, number FROM competition"
                )
                return cursor.fetchall()
        except Exception as e:
            print(f"Query failed: {e}")
            return []
    
    @staticmethod
    def get_competitions_by_type(type: str):
        """Get all competitions"""
        try:
            with get_db_cursor(commit=False) as cursor:
                cursor.execute(
                    """
                    SELECT competition_id, created_time, end_time, status, type, number
                    FROM competition
                    WHERE type = %s
                    """,
                    (type,)
                )
                return cursor.fetchall()
        except Exception as e:
            print(f"Query failed: {e}")
            return []
        
    @staticmethod
    def insert(created_time: date, end_time: date, status: str, type: str, number: int) -> int:
        """Insert a new competition record"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO competition 
                    (created_time, end_time, status, type, number)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING competition_id
                    """,
                    (created_time, end_time, status, type, number)
                )
                result = cursor.fetchone()
                return result['competition_id'] if result else None
        except Exception as e:
            print(f"Insert failed: {e}")
            raise e
        
    @staticmethod
    def get_min_number_by_type(competition_type: str) -> int:
        """Return the minimum number for a specific competition type"""
        try:
            with get_db_cursor(commit=False) as cursor:
                cursor.execute(
                    """
                    SELECT MAX(number) as min_number
                    FROM competition
                    WHERE type = %s
                    """,
                    (competition_type,)
                )
                result = cursor.fetchone()
                return result['min_number'] if result and result['min_number'] is not None else None
        except Exception as e:
            print(f"Query failed: {e}")
            return None
        
    def set_published(competition_id: int):
        """Set competition as published"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE competition
                    SET status = 'Published'
                    WHERE competition_id = %s
                    """,
                    (competition_id,)
                )
        except Exception as e:
            print(f"Update failed: {e}")
            raise e
        
    
    