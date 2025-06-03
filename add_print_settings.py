from app import app
from database import db
from models import PrintSetting
import json

def create_print_settings_table():
    """创建打印设置表并初始化默认数据"""
    with app.app_context():
        # 检查表是否已存在
        try:
            # 检查是否已有打印设置记录
            existing_setting = PrintSetting.query.first()
            if existing_setting:
                print("打印设置表已存在且已有数据，无需创建。")
                return
        except:
            print("打印设置表不存在，正在创建...")
        
        # 创建表
        db.create_all()
        
        # 创建默认打印设置记录
        default_setting = PrintSetting(
            semester="",
            period_times=json.dumps({
                "1": "08:00-08:45", 
                "2": "08:55-09:40", 
                "3": "10:00-10:45",
                "4": "10:55-11:40",
                "5": "14:00-14:45",
                "6": "14:55-15:40",
                "7": "15:50-16:35",
                "8": "16:45-17:30"
            }, ensure_ascii=False),
            common_periods=json.dumps({
                "1": {"name": "课间操", "time": "09:40-10:00"},
                "2": {"name": "午休", "time": "12:00-14:00"},
                "3": {"name": "眼保健操", "time": "15:40-15:50"}
            }, ensure_ascii=False),
            show_additional_info=True,
            font_size="14",
            content_adjust="normal"
        )
        
        # 保存到数据库
        db.session.add(default_setting)
        db.session.commit()
        print("打印设置表创建成功并添加了默认数据。")

if __name__ == "__main__":
    create_print_settings_table()
    print("数据库更新完成") 