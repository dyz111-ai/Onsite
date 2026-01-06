#!/usr/bin/env python3
# 添加 server_port 字段到 training_task 表

from app.database import get_db_cursor

def add_server_port_column():
    """添加 server_port 字段"""
    try:
        with get_db_cursor() as cursor:
            # 检查字段是否已存在
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='training_task' AND column_name='server_port'
            """)
            
            if cursor.fetchone():
                print("字段 server_port 已存在，无需添加")
                return
            
            # 添加字段
            cursor.execute("""
                ALTER TABLE training_task 
                ADD COLUMN server_port INTEGER
            """)
            
            print("成功添加 server_port 字段到 training_task 表")
    except Exception as e:
        print(f"添加字段失败: {e}")
        raise

if __name__ == '__main__':
    add_server_port_column()
