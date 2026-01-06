import psycopg2
import pandas as pd  # 可选，用于美化输出

# 连接信息
connection_info = {
    "host": "shuttle.proxy.rlwy.net",
    "port": "36158",
    "database": "railway",
    "user": "postgres",
    "password": "gSUlaJNbsKWNcZUwRjQUUqjlxeuuAqkV"
}

try:
    # 建立连接
    conn = psycopg2.connect(**connection_info)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("数据库中的表列表")
    print("=" * 60)
    
    # 方法1：查询所有表（公共模式）
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    
    tables = cursor.fetchall()
    
    print(f"找到 {len(tables)} 个表:")
    print("-" * 40)
    
    for i, (table_name,) in enumerate(tables, 1):
        print(f"{i:3d}. {table_name}")
    
    print("-" * 40)
    
    # 如果需要查看每个表的列信息
    for table_name in [table[0] for table in tables]:
        print(f"\n表: {table_name}")
        print("-" * 30)
        
        # 获取表的列信息
        cursor.execute(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        
        for col_name, data_type, is_nullable in columns:
            nullable = "NULL" if is_nullable == 'YES' else "NOT NULL"
            print(f"  {col_name:20} {data_type:20} {nullable}")
    
    # 关闭连接
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"错误: {e}")