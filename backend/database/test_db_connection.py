#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试数据库连接
"""
import psycopg2
from app.database import DB_CONFIG
from datetime import datetime


def test_database_connection():
    """测试数据库连接"""
    
    print("=" * 60)
    print("数据库连接测试")
    print("=" * 60)
    
    # 显示配置信息（隐藏密码）
    print("\n当前数据库配置:")
    print(f"  主机: {DB_CONFIG['host']}")
    print(f"  端口: {DB_CONFIG['port']}")
    print(f"  数据库: {DB_CONFIG['database']}")
    print(f"  用户: {DB_CONFIG['user']}")
    print(f"  密码: {'*' * len(DB_CONFIG['password'])}")
    
    print("\n开始测试连接...")
    
    try:
        # 尝试连接
        start_time = datetime.now()
        conn = psycopg2.connect(**DB_CONFIG)
        end_time = datetime.now()
        
        connection_time = (end_time - start_time).total_seconds() * 1000
        
        print(f"✓ 连接成功！ (耗时: {connection_time:.2f}ms)")
        
        # 获取数据库版本
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"\n数据库版本:")
        print(f"  {version}")
        
        # 获取当前时间
        cursor.execute("SELECT NOW();")
        db_time = cursor.fetchone()[0]
        print(f"\n数据库时间:")
        print(f"  {db_time}")
        
        # 获取所有表
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        print(f"\n数据库表 (共 {len(tables)} 个):")
        for (table_name,) in tables:
            # 获取表的行数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  - {table_name}: {count} 行")
        
        # 测试查询速度
        print("\n测试查询速度:")
        test_queries = [
            ("SELECT 1", "简单查询"),
            ("SELECT COUNT(*) FROM information_schema.tables", "统计表数量"),
        ]
        
        for query, description in test_queries:
            start = datetime.now()
            cursor.execute(query)
            cursor.fetchall()
            end = datetime.now()
            query_time = (end - start).total_seconds() * 1000
            print(f"  {description}: {query_time:.2f}ms")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！数据库连接正常")
        print("=" * 60)
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n✗ 连接失败 (OperationalError):")
        print(f"  {e}")
        print("\n可能的原因:")
        print("  1. 主机地址或端口错误")
        print("  2. 数据库名称错误")
        print("  3. 用户名或密码错误")
        print("  4. 网络不通或防火墙阻止")
        print("  5. 数据库服务未启动")
        return False
        
    except psycopg2.Error as e:
        print(f"\n✗ 数据库错误:")
        print(f"  {e}")
        return False
        
    except Exception as e:
        print(f"\n✗ 未知错误:")
        print(f"  {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    test_database_connection()
