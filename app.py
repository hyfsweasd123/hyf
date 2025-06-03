from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
import json
import csv
import io
from jinja2 import select_autoescape

# 从database.py导入db和login_manager
from database import db, login_manager

# 创建应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # 在生产环境中应该使用一个更复杂的密钥
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school_schedule.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 禁用模板缓存，确保开发时能看到最新的模板
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# 启用Jinja2循环控制扩展，以支持break/continue等标签
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

# 添加自定义过滤器
@app.template_filter('grade_to_text')
def grade_to_text(grade):
    """将年级数字转换为中文显示"""
    grade_map = {
        7: '初一',
        8: '初二',
        9: '初三',
        10: '高一',
        11: '高二',
        12: '高三'
    }
    try:
        grade_num = int(grade)
        return grade_map.get(grade_num, str(grade))
    except (ValueError, TypeError):
        return str(grade)

# 初始化db和login_manager
db.init_app(app)
login_manager.init_app(app)

# 引入模型
from models import User, Teacher, Subject, Class, ClassCombination, TeachingPlan, Schedule, ScheduleSetting, SelfStudyPlan, SubstitutionArrangement, TemporarySubstitution

# 创建数据库表并初始化管理员账户
with app.app_context():
    db.create_all()
    
    # 检查是否已存在管理员用户
    if not User.query.filter_by(role='admin').first():
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            name='系统管理员',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print('已创建管理员账户')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 首页路由
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('用户名或密码错误!', 'danger')
    
    return render_template('login.html')

# 注销
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# 仪表板
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# 初始化数据库
@app.cli.command('init-db')
def init_db_command():
    db.create_all()
    
    # 检查是否已存在管理员用户
    if not User.query.filter_by(role='admin').first():
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            name='系统管理员',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
    
    print('数据库初始化完成!')

# 导入所有蓝图
from routes.users import users_bp
from routes.teachers import teachers_bp
from routes.subjects import subjects_bp
from routes.classes import classes_bp
from routes.class_combinations import combinations_bp
from routes.plans import plans_bp
from routes.schedule import schedule_bp
from routes.selfstudy import selfstudy_bp
from routes.substitution import substitution_bp
from routes.non_routine_sub import non_routine_bp

# 注册蓝图
app.register_blueprint(users_bp)
app.register_blueprint(teachers_bp)
app.register_blueprint(subjects_bp)
app.register_blueprint(classes_bp)
app.register_blueprint(combinations_bp)
app.register_blueprint(plans_bp)
app.register_blueprint(schedule_bp)
app.register_blueprint(selfstudy_bp)
app.register_blueprint(substitution_bp)
app.register_blueprint(non_routine_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5001)