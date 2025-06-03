from app import app
from models import Class, Teacher, Subject, db
import random

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/school_schedule.db'
db.init_app(app)

with app.app_context():
    print("开始添加测试数据...")
    
    # 获取所有班级、学科和教师
    classes = Class.query.all()
    subjects = Subject.query.all()
    teachers = Teacher.query.all()
    
    if not classes:
        print("没有班级数据，请先添加班级")
        exit()
    
    if not subjects:
        print("没有学科数据，请先添加学科")
        exit()
    
    if not teachers:
        print("没有教师数据，请先添加教师")
        exit()
    
    print(f"找到 {len(classes)} 个班级, {len(subjects)} 个学科, {len(teachers)} 个教师")
    
    # 为每个班级的每个学科随机分配教师和课时
    added_count = 0
    for cls in classes:
        print(f"处理班级 {cls.name}...")
        
        # 先删除该班级已有的授课计划
        existing_plans = TeachingPlan.query.filter_by(class_id=cls.id).all()
        for plan in existing_plans:
            db.session.delete(plan)
        
        for subject in subjects:
            # 查找教授该学科的教师
            suitable_teachers = [t for t in teachers if subject in t.subjects]
            if not suitable_teachers:
                # 如果没有教师教授该学科，随机选一个并添加学科关联
                teacher = random.choice(teachers)
                teacher.subjects.append(subject)
                suitable_teachers = [teacher]
            
            # 随机选择一个教师
            teacher = random.choice(suitable_teachers)
            
            # 随机生成课时数(1-6)
            hours = random.randint(1, 6)
            
            # 创建授课计划
            plan = TeachingPlan(
                class_id=cls.id,
                subject_id=subject.id,
                teacher_id=teacher.id,
                hours_per_week=hours,
                is_combined=False
            )
            
            db.session.add(plan)
            added_count += 1
    
    # 提交更改
    db.session.commit()
    print(f"成功添加 {added_count} 条测试授课计划数据") 
    
    # 显示每个班级的总课时数
    print("\n--- 班级总课时统计 ---")
    for cls in classes:
        # 获取该班级的所有授课计划
        plans = TeachingPlan.query.filter_by(class_id=cls.id).all()
        # 使用模型的total_hours属性计算总课时
        total_hours = sum(plan.total_hours for plan in plans)
        print(f"班级 {cls.name}: {total_hours} 课时/周")
    print("--------------------") 

# 测试数据添加脚本
def add_test_classes():
    # 检查是否已有班级数据
    existing_classes = Class.query.all()
    if existing_classes:
        print(f"已存在 {len(existing_classes)} 个班级，跳过添加")
        for cls in existing_classes:
            print(f"- {cls.name} (年级: {cls.grade})")
        return
    
    # 创建测试班级数据
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
    
    # 添加班级数据
    for class_data in test_classes:
        class_obj = Class(
            name=class_data["name"],
            grade=class_data["grade"]
        )
        db.session.add(class_obj)
    
    # 提交到数据库
    db.session.commit()
    print(f"已添加 {len(test_classes)} 个测试班级")

# 仅当直接运行此文件时执行
if __name__ == "__main__":
    with app.app_context():
        add_test_classes() 