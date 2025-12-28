import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

# 数据库连接配置
DB_CONFIG = {
    "host": "shuttle.proxy.rlwy.net",
    "port": "36158",
    "database": "railway",
    "user": "postgres",
    "password": "gSUlaJNbsKWNcZUwRjQUUqjlxeuuAqkV"
}

@contextmanager
def get_db_connection():
    """获取数据库连接的上下文管理器"""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

@contextmanager
def get_db_cursor(commit=True):
    """获取数据库游标的上下文管理器"""
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
            if commit:
                conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
