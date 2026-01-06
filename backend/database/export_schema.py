#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
导出数据库建表SQL脚本
"""
import psycopg2
from app.database import DB_CONFIG
from datetime import datetime


def export_database_schema():
    """导出数据库的所有表结构为SQL"""
    
    try:
        # 连接数据库
        conn = psycopg2.connect(**DB_CONFIG)
        
        cursor = conn.cursor()
        
        # 生成输出文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'database_schema_{timestamp}.sql'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # 写入文件头
            f.write("-- =============================================\n")
            f.write(f"-- 数据库建表SQL导出\n")
            f.write(f"-- 导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"-- 数据库: {DB_CONFIG['database']}\n")
            f.write("-- =============================================\n\n")
            
            # 获取所有表名
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)
            
            tables = cursor.fetchall()
            
            print(f"找到 {len(tables)} 个表")
            
            for (table_name,) in tables:
                print(f"正在导出表: {table_name}")
                
                try:
                    f.write(f"\n-- =============================================\n")
                    f.write(f"-- 表: {table_name}\n")
                    f.write(f"-- =============================================\n\n")
                    
                    # 获取建表语句
                    cursor.execute(f"""
                        SELECT 
                            'CREATE TABLE ' || table_name || ' (' || 
                            string_agg(
                                column_name || ' ' || 
                                CASE 
                                    WHEN data_type = 'character varying' THEN 'VARCHAR(' || character_maximum_length || ')'
                                    WHEN data_type = 'character' THEN 'CHAR(' || character_maximum_length || ')'
                                    WHEN data_type = 'numeric' THEN 'NUMERIC(' || numeric_precision || ',' || numeric_scale || ')'
                                    WHEN data_type = 'integer' AND column_default LIKE 'nextval%%' THEN 'SERIAL'
                                    WHEN data_type = 'bigint' AND column_default LIKE 'nextval%%' THEN 'BIGSERIAL'
                                    WHEN data_type = 'integer' THEN 'INTEGER'
                                    WHEN data_type = 'bigint' THEN 'BIGINT'
                                    WHEN data_type = 'smallint' THEN 'SMALLINT'
                                    WHEN data_type = 'boolean' THEN 'BOOLEAN'
                                    WHEN data_type = 'timestamp without time zone' THEN 'TIMESTAMP'
                                    WHEN data_type = 'timestamp with time zone' THEN 'TIMESTAMPTZ'
                                    WHEN data_type = 'date' THEN 'DATE'
                                    WHEN data_type = 'time without time zone' THEN 'TIME'
                                    WHEN data_type = 'text' THEN 'TEXT'
                                    WHEN data_type = 'json' THEN 'JSON'
                                    WHEN data_type = 'jsonb' THEN 'JSONB'
                                    WHEN data_type = 'uuid' THEN 'UUID'
                                    WHEN data_type = 'double precision' THEN 'DOUBLE PRECISION'
                                    WHEN data_type = 'real' THEN 'REAL'
                                    ELSE UPPER(data_type)
                                END ||
                                CASE 
                                    WHEN is_nullable = 'NO' AND (column_default IS NULL OR column_default NOT LIKE 'nextval%%') THEN ' NOT NULL'
                                    ELSE '' 
                                END ||
                                CASE 
                                    WHEN column_default IS NOT NULL AND column_default NOT LIKE 'nextval%%' THEN ' DEFAULT ' || column_default 
                                    ELSE '' 
                                END,
                                E',\\n    '
                                ORDER BY ordinal_position
                            ) || 
                            ')' as create_statement
                        FROM information_schema.columns
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                        GROUP BY table_name
                    """, (table_name,))
                    
                    result = cursor.fetchone()
                    if result:
                        create_statement = result[0]
                        f.write(f"DROP TABLE IF EXISTS {table_name} CASCADE;\n\n")
                        f.write(create_statement + ";\n\n")
                    else:
                        print(f"  警告: 表 {table_name} 没有列信息")
                        continue
                    
                    # 获取主键
                    cursor.execute("""
                        SELECT constraint_name, column_name
                        FROM information_schema.key_column_usage
                        WHERE table_schema = 'public'
                        AND table_name = %s
                        AND constraint_name IN (
                            SELECT constraint_name
                            FROM information_schema.table_constraints
                            WHERE table_schema = 'public'
                            AND table_name = %s
                            AND constraint_type = 'PRIMARY KEY'
                        )
                        ORDER BY ordinal_position
                    """, (table_name, table_name))
                    
                    pk_columns = cursor.fetchall()
                    if pk_columns:
                        pk_name = pk_columns[0][0]
                        pk_cols = ', '.join([col[1] for col in pk_columns])
                        f.write(f"ALTER TABLE {table_name} ADD CONSTRAINT {pk_name} PRIMARY KEY ({pk_cols});\n\n")
                    
                    # 获取唯一约束
                    cursor.execute("""
                        SELECT tc.constraint_name, string_agg(kcu.column_name, ', ' ORDER BY kcu.ordinal_position)
                        FROM information_schema.table_constraints tc
                        JOIN information_schema.key_column_usage kcu 
                            ON tc.constraint_name = kcu.constraint_name
                            AND tc.table_schema = kcu.table_schema
                        WHERE tc.table_schema = 'public'
                        AND tc.table_name = %s
                        AND tc.constraint_type = 'UNIQUE'
                        GROUP BY tc.constraint_name
                    """, (table_name,))
                    
                    unique_constraints = cursor.fetchall()
                    for constraint_name, columns in unique_constraints:
                        f.write(f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} UNIQUE ({columns});\n\n")
                    
                    # 获取外键
                    cursor.execute("""
                        SELECT
                            tc.constraint_name,
                            kcu.column_name,
                            ccu.table_name AS foreign_table_name,
                            ccu.column_name AS foreign_column_name,
                            rc.update_rule,
                            rc.delete_rule
                        FROM information_schema.table_constraints AS tc
                        JOIN information_schema.key_column_usage AS kcu
                            ON tc.constraint_name = kcu.constraint_name
                            AND tc.table_schema = kcu.table_schema
                        JOIN information_schema.constraint_column_usage AS ccu
                            ON ccu.constraint_name = tc.constraint_name
                            AND ccu.table_schema = tc.table_schema
                        JOIN information_schema.referential_constraints AS rc
                            ON tc.constraint_name = rc.constraint_name
                        WHERE tc.constraint_type = 'FOREIGN KEY'
                        AND tc.table_schema = 'public'
                        AND tc.table_name = %s
                    """, (table_name,))
                    
                    foreign_keys = cursor.fetchall()
                    for fk_name, column, ref_table, ref_column, update_rule, delete_rule in foreign_keys:
                        f.write(f"ALTER TABLE {table_name} ADD CONSTRAINT {fk_name} ")
                        f.write(f"FOREIGN KEY ({column}) REFERENCES {ref_table}({ref_column})")
                        if update_rule != 'NO ACTION':
                            f.write(f" ON UPDATE {update_rule}")
                        if delete_rule != 'NO ACTION':
                            f.write(f" ON DELETE {delete_rule}")
                        f.write(";\n\n")
                    
                    # 获取索引
                    cursor.execute("""
                        SELECT
                            indexname,
                            indexdef
                        FROM pg_indexes
                        WHERE schemaname = 'public'
                        AND tablename = %s
                        AND indexname NOT IN (
                            SELECT constraint_name
                            FROM information_schema.table_constraints
                            WHERE table_schema = 'public'
                            AND table_name = %s
                        )
                    """, (table_name, table_name))
                    
                    indexes = cursor.fetchall()
                    for index_name, index_def in indexes:
                        f.write(f"{index_def};\n\n")
                
                except Exception as e:
                    print(f"  错误: 导出表 {table_name} 失败 - {e}")
                    continue
            
            # 不导出序列，因为SERIAL会自动创建
            # 序列会在使用SERIAL类型时自动创建
        
        cursor.close()
        conn.close()
        
        print(f"\n✓ 导出成功！")
        print(f"文件保存在: {output_file}")
        
    except Exception as e:
        print(f"✗ 导出失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    print("开始导出数据库建表SQL...")
    export_database_schema()
