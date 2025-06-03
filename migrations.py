from flask import Flask
from flask_migrate import Migrate
from database import db
import models

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school_schedule.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

if __name__ == '__main__':
    print("迁移脚本已准备就绪，请使用以下命令运行迁移：")
    print("flask db init  # 首次运行时初始化迁移目录")
    print("flask db migrate -m '移除班级表的班号和学生人数字段'")
    print("flask db upgrade  # 应用迁移到数据库") 