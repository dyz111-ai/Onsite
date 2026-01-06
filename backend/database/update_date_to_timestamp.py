import psycopg2

# 连接信息
connection_info = {
    "host": "shuttle.proxy.rlwy.net",
    "port": "36158",
    "database": "railway",
    "user": "postgres",
    "password": "gSUlaJNbsKWNcZUwRjQUUqjlxeuuAqkV"
}

# 需要修改的表和字段
tables_to_update = [
    {
        "table": "competition",
        "columns": ["created_time", "end_time"]
    },
    {
        "table": "render",
        "columns": ["created_time"]
    }
]

try:
    # 建立连接
    conn = psycopg2.connect(**connection_info)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("开始将 DATE 类型字段修改为 TIMESTAMP 类型")
    print("=" * 60)
    
    for table_info in tables_to_update:
        table_name = table_info["table"]
        columns = table_info["columns"]
        
        print(f"\n处理表: {table_name}")
        print("-" * 40)
        
        for column_name in columns:
            try:
                # 修改字段类型从 DATE 到 TIMESTAMP
                sql = f"""
                    ALTER TABLE {table_name} 
                    ALTER COLUMN {column_name} TYPE TIMESTAMP 
                    USING {column_name}::TIMESTAMP;
                """
                
                cursor.execute(sql)
                conn.commit()
                
                print(f"  ✓ {column_name}: DATE → TIMESTAMP")
                
            except Exception as e:
                print(f"  ✗ {column_name}: 修改失败 - {e}")
                conn.rollback()
    
    print("\n" + "=" * 60)
    print("验证修改结果")
    print("=" * 60)
    
    # 验证修改
    for table_info in tables_to_update:
        table_name = table_info["table"]
        
        cursor.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            AND column_name IN ({','.join([f"'{col}'" for col in table_info['columns']])})
            ORDER BY column_name;
        """)
        
        results = cursor.fetchall()
        
        print(f"\n表: {table_name}")
        for col_name, data_type in results:
            print(f"  {col_name:20} → {data_type}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✓ 所有修改完成！")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ 错误: {e}")
    if conn:
        conn.rollback()
