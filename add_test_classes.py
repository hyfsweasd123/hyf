from app import app
from models import Class, db

# 创建测试班级
test_classes = [
    # 初中班级
    {"name": "初一(1)班", "grade": 7},
    {"name": "初一(2)班", "grade": 7},
    {"name": "初二(1)班", "grade": 8},
    {"name": "初二(2)班", "grade": 8},
    {"name": "初三(1)班", "grade": 9},
    {"name": "初三(2)班", "grade": 9},
    
    # 高中班级
    {"name": "高一(1)班", "grade": 10},
    {"name": "高一(2)班", "grade": 10},
    {"name": "高二(1)班", "grade": 11},
    {"name": "高二(2)班", "grade": 11},
    {"name": "高三(1)班", "grade": 12},
    {"name": "高三(2)班", "grade": 12},
]

with app.app_context():
    # 检查是否已有班级数据
    existing_classes = Class.query.all()
    if existing_classes:
        print(f"已存在 {len(existing_classes)} 个班级:")
        for cls in existing_classes:
            print(f"- {cls.name} (年级: {cls.grade})")
    else:
        # 添加测试班级数据
        for class_data in test_classes:
            class_obj = Class(
                name=class_data["name"],
                grade=class_data["grade"]
            )
            db.session.add(class_obj)
        
        # 提交到数据库
        db.session.commit()
        print(f"已添加 {len(test_classes)} 个测试班级") 