#!/usr/bin/env python
"""检查所有表的外键约束"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, '/Users/jinshaomin/Documents/jinsm/test_hub/grt_testhub')
django.setup()

from django.db import connection

def check_foreign_keys():
    with connection.cursor() as cursor:
        # 获取所有表
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = DATABASE()
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            cursor.execute("""
                SELECT 
                    CONSTRAINT_NAME,
                    DELETE_RULE
                FROM 
                    INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS
                WHERE 
                    TABLE_NAME = %s 
                    AND CONSTRAINT_SCHEMA = DATABASE()
            """, [table])
            
            rows = cursor.fetchall()
            if rows:
                print(f"\n{table}:")
                for row in rows:
                    print(f"  {row[0]}: {row[1]}")

if __name__ == '__main__':
    check_foreign_keys()
