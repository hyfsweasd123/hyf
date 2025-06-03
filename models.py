from database import db
from flask_login import UserMixin
from datetime import datetime

# 用户模型
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin 或 sub_admin
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<User {self.username}>'

# 教师模型
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    gender = db.Column(db.String(10), nullable=True)  # 添加回gender字段但允许为空
    staff_id = db.Column(db.String(20), unique=True, nullable=False)  # 恢复staff_id字段
    max_hours_per_day = db.Column(db.Integer, default=6)  # 每天最大课时数
    subjects = db.relationship('Subject', secondary='teacher_subject')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<Teacher {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'staff_id': self.staff_id,
            'max_hours_per_day': self.max_hours_per_day
        }

# 教师-学科关联表
teacher_subject = db.Table('teacher_subject',
    db.Column('teacher_id', db.Integer, db.ForeignKey('teacher.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True)
)

# 学科模型
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    is_major = db.Column(db.Boolean, default=False)  # 是否为主科
    teachers = db.relationship('Teacher', secondary='teacher_subject', overlaps="subjects")
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<Subject {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'is_major': self.is_major
        }

# 班级模型
class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    grade = db.Column(db.Integer, nullable=False)  # 年级
    head_teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    head_teacher = db.relationship('Teacher')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<Class {self.name}>'

# 合班设置模型
class ClassCombination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    subject = db.relationship('Subject')
    classes = db.relationship('Class', secondary='class_combination_detail')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<ClassCombination {self.name}>'

# 合班详情关联表
class_combination_detail = db.Table('class_combination_detail',
    db.Column('combination_id', db.Integer, db.ForeignKey('class_combination.id'), primary_key=True),
    db.Column('class_id', db.Integer, db.ForeignKey('class.id'), primary_key=True)
)

# 授课计划模型
class TeachingPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    class_obj = db.relationship('Class')
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    subject = db.relationship('Subject')
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    teacher = db.relationship('Teacher')
    hours_per_week = db.Column(db.Integer, nullable=False)  # 每周课时数
    is_combined = db.Column(db.Boolean, default=False)  # 是否为合班
    combination_id = db.Column(db.Integer, db.ForeignKey('class_combination.id'), nullable=True)
    combination = db.relationship('ClassCombination')
    # 单双周设置
    week_type = db.Column(db.String(10), nullable=True)  # 'all': 每周, 's': 单周, 'd': 双周, 'f': 随机
    extra_hours = db.Column(db.Integer, nullable=True)  # 额外课时数(如4s1中的1)
    extra_week_type = db.Column(db.String(10), nullable=True)  # 额外课时的周类型
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # 添加数据库索引以优化查询性能
    __table_args__ = (
        db.Index('idx_class_subject', 'class_id', 'subject_id'),
        db.Index('idx_teacher_class', 'teacher_id', 'class_id'),
        db.Index('idx_class_teacher_subject', 'class_id', 'teacher_id', 'subject_id'),
    )

    def __repr__(self):
        return f'<TeachingPlan {self.class_obj.name}-{self.subject.name}>'

    @property
    def total_hours(self):
        """总课时数（包含额外课时）"""
        total = self.hours_per_week
        if self.extra_hours:
            total += self.extra_hours
        return total

    def to_dict(self):
        return {
            'id': self.id,
            'class_id': self.class_id,
            'subject_id': self.subject_id,
            'subject': self.subject.to_dict() if self.subject else None,
            'teacher_id': self.teacher_id,
            'teacher': self.teacher.to_dict() if self.teacher else None,
            'hours_per_week': self.hours_per_week,
            'is_combined': self.is_combined,
            'combination_id': self.combination_id,
            'week_type': self.week_type,
            'extra_hours': self.extra_hours,
            'extra_week_type': self.extra_week_type,
            'total_hours': self.total_hours
        }

# 排课设置
class ScheduleSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    periods_per_day = db.Column(db.Integer, default=8)  # 每天课时数
    days_per_week = db.Column(db.Integer, default=5)  # 每周上课天数
    morning_periods = db.Column(db.Integer, default=4)  # 上午课时数
    afternoon_periods = db.Column(db.Integer, default=4)  # 下午课时数
    major_subjects_morning = db.Column(db.Boolean, default=True)  # 主科上午排课优先
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

# 课表模型
class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    class_obj = db.relationship('Class')
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    subject = db.relationship('Subject')
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    teacher = db.relationship('Teacher')
    day_of_week = db.Column(db.Integer, nullable=False)  # 1-7 表示周一到周日
    period = db.Column(db.Integer, nullable=False)  # 第几节课
    is_combined = db.Column(db.Boolean, default=False)  # 是否为合班
    combination_id = db.Column(db.Integer, db.ForeignKey('class_combination.id'), nullable=True)
    combination = db.relationship('ClassCombination')
    week_type = db.Column(db.String(10), nullable=False, default='all')  # 'all': 每周, 's': 单周, 'd': 双周
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # 添加数据库索引以优化查询性能
    __table_args__ = (
        db.Index('idx_class_day_period', 'class_id', 'day_of_week', 'period'),
        db.Index('idx_teacher_day_period', 'teacher_id', 'day_of_week', 'period'),
        db.Index('idx_day_period', 'day_of_week', 'period'),
    )

    def __repr__(self):
        week_type_str = "每周" if self.week_type == 'all' else ("单周" if self.week_type == 's' else "双周")
        return f'<Schedule {self.class_obj.name} 周{self.day_of_week} 第{self.period}节 {self.subject.name} {week_type_str}>'

# 学科禁排设置模型
class SubjectBlock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.Integer, nullable=False)  # 1-7 表示周一到周日
    period = db.Column(db.Integer, nullable=False)  # 第几节课
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True)  # 为空表示禁排所有学科
    subject = db.relationship('Subject')
    is_block_all = db.Column(db.Boolean, default=False)  # 是否禁排所有学科
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        if self.is_block_all:
            return f'<SubjectBlock 星期{self.day_of_week} 第{self.period}节 全部禁排>'
        else:
            return f'<SubjectBlock 星期{self.day_of_week} 第{self.period}节 {self.subject.name if self.subject else "未知学科"} 禁排>'

# 公共课程模型
class CommonCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 公共课程名称
    day_of_week = db.Column(db.Integer, nullable=False)  # 1-7 表示周一到周日
    period = db.Column(db.Integer, nullable=False)  # 第几节课
    description = db.Column(db.String(255), nullable=True)  # 课程描述，可选
    apply_to_all_classes = db.Column(db.Boolean, default=True)  # 是否应用于所有班级
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=True)  # 如果不是应用于所有班级，则指定班级
    class_obj = db.relationship('Class')
    week_type = db.Column(db.String(10), nullable=False, default='all')  # 'all': 每周, 's': 单周, 'd': 双周
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        week_type_str = "每周" if self.week_type == 'all' else ("单周" if self.week_type == 's' else "双周")
        class_str = "所有班级" if self.apply_to_all_classes else self.class_obj.name
        return f'<CommonCourse {self.name} 周{self.day_of_week} 第{self.period}节 {week_type_str} 适用于{class_str}>'

# 打印设置模型
class PrintSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_name = db.Column(db.String(100), nullable=True, default="六盘水市第七中学")  # 学校名称
    semester = db.Column(db.String(100), nullable=True)  # 学期信息
    period_times = db.Column(db.Text, nullable=True)  # 每节课的时间（JSON格式）
    common_periods = db.Column(db.Text, nullable=True)  # 公共时段设置（JSON格式）
    
    # 页面格式设置
    row_height = db.Column(db.Integer, default=45)  # 行高（像素）
    column_width = db.Column(db.Integer, default=27)  # 列宽（字符数）
    title_row_height = db.Column(db.Integer, default=25)  # 标题行高（像素）
    
    # 保持与现有打印设置兼容的字段
    show_additional_info = db.Column(db.Boolean, default=True)
    password = db.Column(db.String(100), nullable=True)
    font_size = db.Column(db.String(10), default='14')
    content_adjust = db.Column(db.String(20), default='normal')
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<PrintSetting {self.id} {self.school_name or "未设置学校"} {self.semester if self.semester else "未设置学期"}>'

# 早晚自习授课计划模型
class SelfStudyPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    class_obj = db.relationship('Class')
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    subject = db.relationship('Subject')
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    teacher = db.relationship('Teacher')
    hours_per_week = db.Column(db.Integer, nullable=False)  # 每周课时数
    is_combined = db.Column(db.Boolean, default=False)  # 是否为合班
    combination_id = db.Column(db.Integer, db.ForeignKey('class_combination.id'), nullable=True)
    combination = db.relationship('ClassCombination')
    # 单双周设置
    week_type = db.Column(db.String(10), nullable=True)  # 'all': 每周, 's': 单周, 'd': 双周, 'f': 随机
    extra_hours = db.Column(db.Integer, nullable=True)  # 额外课时数(如4s1中的1)
    extra_week_type = db.Column(db.String(10), nullable=True)  # 额外课时的周类型
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<SelfStudyPlan {self.class_obj.name}-{self.subject.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'class_id': self.class_id,
            'subject_id': self.subject_id,
            'subject': self.subject.to_dict() if self.subject else None,
            'teacher_id': self.teacher_id,
            'teacher': self.teacher.to_dict() if self.teacher else None,
            'hours_per_week': self.hours_per_week,
            'is_combined': self.is_combined,
            'combination_id': self.combination_id,
            'week_type': self.week_type,
            'extra_hours': self.extra_hours,
            'extra_week_type': self.extra_week_type
        }

# 早晚自习课程安排模型
class SelfStudySchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    class_obj = db.relationship('Class')
    day = db.Column(db.Integer, nullable=False)  # 星期几 1-7
    period = db.Column(db.String(20), nullable=False)  # 早读1, 晚修1
    plan_id = db.Column(db.Integer, db.ForeignKey('self_study_plan.id'), nullable=True)  # 使plan_id可为空
    plan = db.relationship('SelfStudyPlan')
    is_common_course = db.Column(db.Boolean, default=False)  # 是否为公共课程
    common_course_title = db.Column(db.String(100), nullable=True)  # 公共课程标题
    common_course_desc = db.Column(db.String(200), nullable=True)  # 公共课程描述
    apply_to_all_classes = db.Column(db.Boolean, default=False)  # 是否应用于所有班级
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    @property
    def subject(self):
        """返回关联计划的学科"""
        return self.plan.subject if self.plan else None
    
    @property
    def teacher(self):
        """返回关联计划的教师"""
        return self.plan.teacher if self.plan else None
    
    def __repr__(self):
        if self.is_common_course:
            return f'<SelfStudySchedule {self.class_obj.name}-{self.day}-{self.period}-公共课程:{self.common_course_title}>'
        else:
            return f'<SelfStudySchedule {self.class_obj.name}-{self.day}-{self.period}>'
    
    def to_dict(self):
        if self.is_common_course:
            return {
                'id': self.id,
                'class_id': self.class_id,
                'day': self.day,
                'period': self.period,
                'is_common_course': True,
                'common_course_title': self.common_course_title,
                'common_course_desc': self.common_course_desc
            }
        else:
            return {
                'id': self.id,
                'class_id': self.class_id,
                'day': self.day,
                'period': self.period,
                'plan_id': self.plan_id,
                'subject': self.subject.name if self.subject else None,
                'teacher': self.teacher.name if self.teacher else None,
                'is_common_course': False
            }

# 早晚自习禁排设置模型
class SelfStudyBlock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    class_obj = db.relationship('Class')
    day = db.Column(db.Integer, nullable=False)  # 星期几 1-7
    period = db.Column(db.String(20), nullable=False)  # 早读1, 晚修1
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<SelfStudyBlock {self.class_obj.name}-{self.day}-{self.period}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'class_id': self.class_id,
            'day': self.day,
            'period': self.period
        }

# 代课安排模型
class SubstitutionArrangement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    original_teacher = db.relationship('Teacher', foreign_keys=[original_teacher_id])
    substitute_teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    substitute_teacher = db.relationship('Teacher', foreign_keys=[substitute_teacher_id])
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    class_obj = db.relationship('Class')
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    subject = db.relationship('Subject')
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<SubstitutionArrangement {self.original_teacher.name} -> {self.substitute_teacher.name}, {self.subject.name}, {self.start_date} 至 {self.end_date}>'

    def to_dict(self):
        return {
            'id': self.id,
            'original_teacher_id': self.original_teacher_id,
            'original_teacher_name': self.original_teacher.name if self.original_teacher else None,
            'substitute_teacher_id': self.substitute_teacher_id,
            'substitute_teacher_name': self.substitute_teacher.name if self.substitute_teacher else None,
            'class_id': self.class_id,
            'class_name': self.class_obj.name if self.class_obj else None,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
            'reason': self.reason,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

# 临时代课模型
class TemporarySubstitution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    original_teacher = db.relationship('Teacher', foreign_keys=[original_teacher_id])
    substitute_teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    substitute_teacher = db.relationship('Teacher', foreign_keys=[substitute_teacher_id])
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    class_obj = db.relationship('Class')
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    subject = db.relationship('Subject')
    date = db.Column(db.Date, nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 1-7 表示周一到周日
    period = db.Column(db.Integer, nullable=False)  # 第几节课
    reason = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, completed
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<TemporarySubstitution {self.original_teacher.name} -> {self.substitute_teacher.name}, {self.subject.name}, {self.date}, 第{self.period}节>'

    def to_dict(self):
        return {
            'id': self.id,
            'original_teacher_id': self.original_teacher_id,
            'original_teacher_name': self.original_teacher.name if self.original_teacher else None,
            'substitute_teacher_id': self.substitute_teacher_id,
            'substitute_teacher_name': self.substitute_teacher.name if self.substitute_teacher else None,
            'class_id': self.class_id,
            'class_name': self.class_obj.name if self.class_obj else None,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'day_of_week': self.day_of_week,
            'period': self.period,
            'reason': self.reason,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

# 常规代课模型
class NonRoutineSubstitution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    original_teacher = db.relationship('Teacher', foreign_keys=[original_teacher_id])
    substitute_teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    substitute_teacher = db.relationship('Teacher', foreign_keys=[substitute_teacher_id])
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    class_obj = db.relationship('Class')
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    subject = db.relationship('Subject')
    date = db.Column(db.Date, nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 1-7 表示周一到周日
    period = db.Column(db.Integer, nullable=False)  # 第几节课
    reason = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)  # 额外备注信息
    status = db.Column(db.String(20), default='pending')  # pending, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<NonRoutineSubstitution {self.original_teacher.name} -> {self.substitute_teacher.name}, {self.subject.name}, {self.date}, 第{self.period}节>'

    def to_dict(self):
        return {
            'id': self.id,
            'original_teacher_id': self.original_teacher_id,
            'original_teacher_name': self.original_teacher.name if self.original_teacher else None,
            'substitute_teacher_id': self.substitute_teacher_id,
            'substitute_teacher_name': self.substitute_teacher.name if self.substitute_teacher else None,
            'class_id': self.class_id,
            'class_name': self.class_obj.name if self.class_obj else None,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'day_of_week': self.day_of_week,
            'period': self.period,
            'reason': self.reason,
            'notes': self.notes,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }