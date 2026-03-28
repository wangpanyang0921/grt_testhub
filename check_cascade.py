#!/usr/bin/env python
"""检查所有 CASCADE 外键约束"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, '/Users/jinshaomin/Documents/jinsm/test_hub/grt_testhub')
django.setup()

from django.db import connection

def check_cascade_foreign_keys():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                TABLE_NAME,
                CONSTRAINT_NAME,
                DELETE_RULE
            FROM 
                INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS
            WHERE 
                CONSTRAINT_SCHEMA = DATABASE()
                AND DELETE_RULE = 'CASCADE'
            ORDER BY TABLE_NAME
        """)
        
        print("所有 CASCADE 外键约束:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} ({row[2]})")

if __name__ == '__main__':
    check_cascade_foreign_keys()
