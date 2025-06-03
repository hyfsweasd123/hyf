from flask import Flask
from database import db
from models import SubstitutionArrangement, TemporarySubstitution
import sqlite3
import traceback

# 初始化应用
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school_schedule.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db.init_app(app)

def check_column_exists(table_name, column_name):
    """检查表中是否存在指定列"""
    conn = sqlite3.connect('school_schedule.db')
    cursor = conn.cursor()
    
    # 查询表结构
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in cursor.fetchall()]
    
    conn.close()
    
    return column_name in columns

def check_table_exists(table_name):
    """检查表是否存在"""
    conn = sqlite3.connect('school_schedule.db')
    cursor = conn.cursor()
    
    # 查询所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [table[0] for table in cursor.fetchall()]
    
    conn.close()
    
    return table_name in tables

def run_migration():
    """执行迁移"""
    with app.app_context():
        try:
            # 检查代课安排表是否存在
            if not check_table_exists('substitution_arrangement'):
                print("创建代课安排表...")
                db.create_all(tables=[SubstitutionArrangement.__table__])
                print("代课安排表创建成功!")
            else:
                print("代课安排表已存在.")
            
            # 检查临时代课表是否存在
            if not check_table_exists('temporary_substitution'):
                print("创建临时代课表...")
                db.create_all(tables=[TemporarySubstitution.__table__])
                print("临时代课表创建成功!")
            else:
                print("临时代课表已存在.")
            
            print("数据库迁移完成!")
            
        except Exception as e:
            print(f"迁移出错: {str(e)}")
            traceback.print_exc()

if __name__ == '__main__':
    run_migration() 