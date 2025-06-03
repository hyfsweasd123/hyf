from app import app, db
from sqlalchemy import text
from flask_migrate import Migrate

migrate = Migrate(app, db)

if __name__ == '__main__':
    with app.app_context():
        print("开始迁移数据库...")
        # 添加apply_to_all_classes字段
        db.session.execute(text('ALTER TABLE self_study_schedule ADD COLUMN apply_to_all_classes BOOLEAN DEFAULT 0'))
        db.session.commit()
        print("数据库迁移完成！") 