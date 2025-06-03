from database import db
from models import TeachingPlan, Class, Subject, Teacher
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/school_schedule.db'
db.init_app(app)

with app.app_context():
    # 检查班级数据
    classes = Class.query.all()
    print(f"班级数量: {len(classes)}")
    if classes:
        print(f"班级示例: {[c.name for c in classes[:5]]}")
    
    # 检查排课计划数据
    plans = TeachingPlan.query.all()
    print(f"排课计划总数: {len(plans)}")
    
    # 检查特定班级的排课计划
    if classes:
        class_id = classes[0].id
        class_plans = TeachingPlan.query.filter_by(class_id=class_id).all()
        print(f"班级ID {class_id} ({classes[0].name}) 的排课计划数: {len(class_plans)}")
        
        if class_plans:
            print("排课计划示例:")
            for plan in class_plans[:5]:
                print(f"  学科: {plan.subject.name}, 教师: {plan.teacher.name}, 课时: {plan.hours_per_week}")
        else:
            print("该班级没有排课计划数据")
    
    # 检查学科和教师数据
    subjects = Subject.query.all()
    teachers = Teacher.query.all()
    print(f"学科总数: {len(subjects)}")
    print(f"教师总数: {len(teachers)}") 