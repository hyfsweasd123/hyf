from app import app
from database import db
from models import Teacher

def fix_max_hours_per_day():
    with app.app_context():
        # 获取所有教师
        teachers = Teacher.query.all()
        fixed_count = 0
        
        print(f"检查 {len(teachers)} 个教师的每日最大课时数...")
        
        for teacher in teachers:
            # 检查max_hours_per_day是否为None
            if teacher.max_hours_per_day is None:
                teacher.max_hours_per_day = 6  # 设置默认值为6
                fixed_count += 1
                print(f"修复: 教师 {teacher.name} 的每日最大课时数设为6")
        
        # 提交更改
        if fixed_count > 0:
            db.session.commit()
            print(f"成功修复 {fixed_count} 个教师的每日最大课时数")
        else:
            print("所有教师的每日最大课时数都已设置，无需修复")

if __name__ == "__main__":
    fix_max_hours_per_day() 