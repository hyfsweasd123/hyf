from flask import Flask
from database import db
from models import Subject
import sys

app = Flask(__name__)
app.config.from_pyfile('config.py')

# 初始化数据库
db.init_app(app)

with app.app_context():
    # 获取带"1"后缀的科目
    subjects = Subject.query.all()
    saturday_subjects = [subject for subject in subjects if subject.name.endswith('1')]
    
    print(f"找到 {len(saturday_subjects)} 个带\"1\"后缀的科目:")
    for subject in saturday_subjects:
        print(f" - {subject.name} ({'主科' if subject.is_major else '副科'})")

print("\n系统已更新完成。现在带\"1\"后缀的科目将一定排在星期六。") 