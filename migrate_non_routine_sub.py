from app import app, db
from models import NonRoutineSubstitution
from datetime import datetime
from sqlalchemy import inspect

def migrate_non_routine_substitution():
    """创建非常规代课表"""
    print("开始迁移非常规代课表...")
    
    with app.app_context():
        # 使用inspect来检查表是否存在
        inspector = inspect(db.engine)
        table_exists = inspector.has_table('non_routine_substitution')
        
        if not table_exists:
            db.create_all()
            print("非常规代课表创建成功")
        else:
            print("非常规代课表已存在")
    
    print("非常规代课表迁移完成")

if __name__ == '__main__':
    migrate_non_routine_substitution() 