import sqlite3
import os

def fix_database():
    print("开始修复数据库...")
    
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
        
        # 检查subject表的列
        cursor.execute("PRAGMA table_info(subject)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # 如果没有is_major列，添加它
        if 'is_major' not in columns:
            print("添加is_major列到subject表...")
            cursor.execute("ALTER TABLE subject ADD COLUMN is_major BOOLEAN DEFAULT FALSE")
            
            # 设置主科
            major_subjects = ['语文', '数学', '英语', '物理', '化学', '政治', '历史', '生物', '地理']
            for subject in major_subjects:
                cursor.execute("UPDATE subject SET is_major = 1 WHERE name = ?", (subject,))
                if cursor.rowcount > 0:
                    print(f"已将 {subject} 设置为主科")
        else:
            print("subject表已有is_major列")
        
        # 检查teacher表的列
        cursor.execute("PRAGMA table_info(teacher)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # 如果没有max_hours_per_day列，添加它
        if 'max_hours_per_day' not in columns:
            print("添加max_hours_per_day列到teacher表...")
            cursor.execute("ALTER TABLE teacher ADD COLUMN max_hours_per_day INTEGER DEFAULT 6")
        else:
            print("teacher表已有max_hours_per_day列")
        
        # 提交更改
        conn.commit()
        print("数据库修复完成！")
        
    except Exception as e:
        print(f"修复数据库时出错: {str(e)}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    fix_database() 