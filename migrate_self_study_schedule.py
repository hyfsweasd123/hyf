from app import app, db
from sqlalchemy import text
from flask_migrate import Migrate

migrate = Migrate(app, db)

if __name__ == '__main__':
    with app.app_context():
        print("开始迁移数据库...")
        # 使用text()函数包装SQL语句
        db.session.execute(text('ALTER TABLE self_study_schedule ADD COLUMN is_common_course BOOLEAN DEFAULT 0'))
        db.session.execute(text('ALTER TABLE self_study_schedule ADD COLUMN common_course_title VARCHAR(100)'))
        db.session.execute(text('ALTER TABLE self_study_schedule ADD COLUMN common_course_desc VARCHAR(200)'))
        db.session.commit()
        print("数据库迁移完成！") 