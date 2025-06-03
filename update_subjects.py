from app import app
from database import db
from models import Subject
from sqlalchemy import text
import sys

# 定义主科列表
MAJOR_SUBJECTS = ['语文', '数学', '英语', '物理', '化学', '政治', '历史', '生物', '地理']

def update_subjects():
    with app.app_context():
        # 更新数据库结构
        try:
            # 使用text执行SQL语句
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE subject ADD COLUMN IF NOT EXISTS is_major BOOLEAN DEFAULT FALSE'))
                conn.commit()
            print("成功添加 is_major 字段到 subject 表")
        except Exception as e:
            print(f"字段可能已存在或其他错误: {e}")
            
        # 设置主科
        subjects = Subject.query.all()
        updated_count = 0
        
        for subject in subjects:
            if subject.name in MAJOR_SUBJECTS:
                subject.is_major = True
                updated_count += 1
                print(f"设置 {subject.name} 为主科")
            else:
                subject.is_major = False
                
        db.session.commit()
        print(f"成功更新 {updated_count} 个主科")
        
        # 显示所有科目
        all_subjects = Subject.query.all()
        print("\n所有科目:")
        for subject in all_subjects:
            print(f"{subject.name}: {'主科' if subject.is_major else '副科'}")

        # 显示带"1"后缀的科目
        saturday_subjects = [subject for subject in all_subjects if subject.name.endswith('1')]
        print(f"\n找到 {len(saturday_subjects)} 个带\"1\"后缀的科目:")
        for subject in saturday_subjects:
            print(f"{subject.name}: {'主科' if subject.is_major else '副科'}")
        print("\n系统已更新完成。现在带\"1\"后缀的科目将一定排在星期六（篮球1和足球1除外）。")

if __name__ == "__main__":
    update_subjects()
    print("数据库更新完成") 