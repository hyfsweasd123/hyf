from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# 初始化数据库
db = SQLAlchemy()

# 初始化登录管理器
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = '请先登录!' 