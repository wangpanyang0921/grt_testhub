#!/usr/bin/env python
"""修复 testcases 表的外键约束，使用 SET NULL 而不是 NO ACTION"""

import os
import sys
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, '/Users/jinshaomin/Documents/jinsm/test_hub/grt_testhub')
django.setup()

from django.db import connection

def fix_foreign_keys():
    with connection.cursor() as cursor:
        print("开始修复外键约束...")
        
        # 1. 删除旧的 project_id 外键约束
        try:
            cursor.execute("ALTER TABLE testcases DROP FOREIGN KEY testcases_project_id_e201e15a_fk_projects_id")
            print("✓ 已删除旧的 project_id 外键约束")
        except Exception as e:
            print(f"✗ 删除旧的 project_id 外键约束失败: {e}")
        
        # 2. 添加新的 project_id 外键约束，使用 SET NULL
        try:
            cursor.execute("""
                ALTER TABLE testcases 
                ADD CONSTRAINT testcases_project_id_fk 
                FOREIGN KEY (project_id) REFERENCES projects(id) 
                ON DELETE SET NULL
            """)
            print("✓ 已添加新的 project_id 外键约束 (SET NULL)")
        except Exception as e:
            print(f"✗ 添加新的 project_id 外键约束失败: {e}")
        
        # 3. 删除旧的 menu_id 外键约束
        try:
            cursor.execute("ALTER TABLE testcases DROP FOREIGN KEY testcases_menu_id_f60747a7_fk_project_menus_id")
            print("✓ 已删除旧的 menu_id 外键约束")
        except Exception as e:
            print(f"✗ 删除旧的 menu_id 外键约束失败: {e}")
        
        # 4. 添加新的 menu_id 外键约束，使用 SET NULL
        try:
            cursor.execute("""
                ALTER TABLE testcases 
                ADD CONSTRAINT testcases_menu_id_fk 
                FOREIGN KEY (menu_id) REFERENCES project_menus(id) 
                ON DELETE SET NULL
            """)
            print("✓ 已添加新的 menu_id 外键约束 (SET NULL)")
        except Exception as e:
            print(f"✗ 添加新的 menu_id 外键约束失败: {e}")
        
        print("\n外键约束修复完成！")
        
        # 验证新的外键约束
        cursor.execute("""
            SELECT 
                CONSTRAINT_NAME,
                DELETE_RULE
            FROM 
                INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS
            WHERE 
                TABLE_NAME = 'testcases' 
                AND CONSTRAINT_SCHEMA = DATABASE()
        """)
        
        print("\n当前 testcases 表的外键删除规则:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")

if __name__ == '__main__':
    fix_foreign_keys()
