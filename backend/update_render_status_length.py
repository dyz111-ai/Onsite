import psycopg2

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
    print("修改 render 表的 status 字段长度")
    print("=" * 60)
    
    # 修改 status 字段长度从 VARCHAR(10) 到 VARCHAR(20)
    print("\n正在修改 status 字段长度: VARCHAR(10) → VARCHAR(20)")
    
    cursor.execute("""
        ALTER TABLE render 
        ALTER COLUMN status TYPE VARCHAR(20);
    """)
    
    conn.commit()
    print("✓ 修改成功")
    
    # 验证修改
    print("\n" + "=" * 60)
    print("验证修改结果")
    print("=" * 60)
    
    cursor.execute("""
        SELECT column_name, data_type, character_maximum_length
        FROM information_schema.columns 
        WHERE table_name = 'render' 
        AND column_name = 'status';
    """)
    
    result = cursor.fetchone()
    
    if result:
        col_name, data_type, max_length = result
        print(f"\n表: render")
        print(f"  字段名: {col_name}")
        print(f"  数据类型: {data_type}")
        print(f"  最大长度: {max_length}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✓ 修改完成！")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ 错误: {e}")
    if conn:
        conn.rollback()
