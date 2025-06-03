import sqlite3
import os

def migrate_database():
    print("开始数据库迁移...")
    
    # 数据库文件路径
    db_path = 'instance/school_schedule.db'
    
    # 检查数据库文件是否存在
    if not os.path.exists(db_path):
        print(f"错误: 数据库文件 '{db_path}' 不存在")
        return
    
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查是否需要迁移subject表
        cursor.execute("PRAGMA table_info(subject)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'code' in column_names:
            print("迁移subject表，移除code字段...")
            # 创建临时表，不包含code字段
            cursor.execute('''
                CREATE TABLE subject_temp (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(80) NOT NULL UNIQUE,
                    created_at DATETIME,
                    updated_at DATETIME
                )
            ''')
            
            # 复制数据
            cursor.execute('''
                INSERT INTO subject_temp (id, name, created_at, updated_at)
                SELECT id, name, created_at, updated_at FROM subject
            ''')
            
            # 删除原表并重命名临时表
            cursor.execute("DROP TABLE subject")
            cursor.execute("ALTER TABLE subject_temp RENAME TO subject")
            
            print("subject表迁移完成")
        
        # 检查subject表是否有is_major字段
        cursor.execute("PRAGMA table_info(subject)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'is_major' not in column_names:
            print("正在更新subject表，添加is_major字段...")
            cursor.execute("ALTER TABLE subject ADD COLUMN is_major BOOLEAN DEFAULT FALSE")
            
            # 设置主科
            major_subjects = ['语文', '数学', '英语', '物理', '化学', '政治', '历史', '生物', '地理']
            
            for subject_name in major_subjects:
                cursor.execute("UPDATE subject SET is_major = TRUE WHERE name = ?", (subject_name,))
                rows_affected = cursor.rowcount
                if rows_affected > 0:
                    print(f"已将 {subject_name} 设置为主科")
            
            print("subject表is_major字段更新完成")
        else:
            print("subject表已包含is_major字段，无需迁移")
            
        # 检查teacher表是否有max_hours_per_day字段
        cursor.execute("PRAGMA table_info(teacher)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'max_hours_per_day' not in column_names:
            print("正在更新teacher表，添加max_hours_per_day字段...")
            cursor.execute("ALTER TABLE teacher ADD COLUMN max_hours_per_day INTEGER DEFAULT 6")
            print("teacher表max_hours_per_day字段更新完成")
        else:
            print("teacher表已包含max_hours_per_day字段，无需迁移")
            
        # 检查TeachingPlan表是否需要添加单双周字段
        cursor.execute("PRAGMA table_info(teaching_plan)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'week_type' not in column_names:
            print("正在更新TeachingPlan表，添加单双周字段...")
            cursor.execute("ALTER TABLE teaching_plan ADD COLUMN week_type VARCHAR(10)")
            cursor.execute("ALTER TABLE teaching_plan ADD COLUMN extra_hours INTEGER")
            cursor.execute("ALTER TABLE teaching_plan ADD COLUMN extra_week_type VARCHAR(10)")
            
            # 设置默认值
            cursor.execute("UPDATE teaching_plan SET week_type = 'all'")
            print("TeachingPlan表更新完成")
        
        # 检查Schedule表是否需要添加单双周字段
        cursor.execute("PRAGMA table_info(schedule)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'week_type' not in column_names:
            print("正在更新Schedule表，添加单双周字段...")
            cursor.execute("ALTER TABLE schedule ADD COLUMN week_type VARCHAR(10) NOT NULL DEFAULT 'all'")
            print("Schedule表更新完成")
            
        # 检查是否需要迁移class表
        cursor.execute("PRAGMA table_info(class)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'class_number' in column_names or 'student_count' in column_names:
            print("迁移class表，移除class_number和student_count字段...")
            # 创建临时表
            cursor.execute('''
                CREATE TABLE class_temp (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(80) NOT NULL UNIQUE,
                    grade INTEGER NOT NULL,
                    head_teacher_id INTEGER,
                    created_at DATETIME,
                    updated_at DATETIME,
                    FOREIGN KEY (head_teacher_id) REFERENCES teacher (id)
                )
            ''')
            
            # 复制数据
            cursor.execute('''
                INSERT INTO class_temp (id, name, grade, head_teacher_id, created_at, updated_at)
                SELECT id, name, grade, head_teacher_id, created_at, updated_at FROM class
            ''')
            
            # 删除原表
            cursor.execute('DROP TABLE class')
            
            # 重命名临时表为原表
            cursor.execute('ALTER TABLE class_temp RENAME TO class')
            
            print("成功移除class表中的class_number和student_count字段")
        else:
            print("class表已经是最新结构，无需迁移")
            
        # 重建teacher_subject关系表
        print("更新teacher_subject关系表...")
        cursor.execute("DROP TABLE IF EXISTS teacher_subject")
        cursor.execute('''
            CREATE TABLE teacher_subject (
                teacher_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                PRIMARY KEY (teacher_id, subject_id),
                FOREIGN KEY (teacher_id) REFERENCES teacher (id),
                FOREIGN KEY (subject_id) REFERENCES subject (id)
            )
        ''')
        
        # 提交更改
        conn.commit()
        print("数据库迁移成功完成!")
        
    except Exception as e:
        print(f"迁移数据库时出错: {str(e)}")
    finally:
        # 关闭数据库连接
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_database() 