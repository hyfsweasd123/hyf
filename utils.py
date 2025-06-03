"""
工具函数模块
包含系统中常用的辅助函数
"""

import logging
import time
from functools import wraps
from typing import List, Optional, Dict, Any
from models import TeachingPlan, Schedule
from sqlalchemy.orm import joinedload


def log_performance(func):
    """性能监控装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f'{func.__name__} took {end_time - start_time:.2f} seconds')
        return result
    return wrapper


def calculate_class_total_hours(class_id: int) -> int:
    """
    计算指定班级的总课时数
    
    Args:
        class_id: 班级ID
        
    Returns:
        int: 总课时数
    """
    plans = TeachingPlan.query.filter_by(class_id=class_id).all()
    return sum(plan.total_hours for plan in plans)


def get_teaching_plans_optimized(class_id: Optional[int] = None) -> List[TeachingPlan]:
    """
    优化的授课计划查询，使用joinedload避免N+1查询
    
    Args:
        class_id: 班级ID，如果为None则查询所有
        
    Returns:
        List[TeachingPlan]: 授课计划列表
    """
    query = TeachingPlan.query.options(
        joinedload(TeachingPlan.subject),
        joinedload(TeachingPlan.teacher),
        joinedload(TeachingPlan.class_obj)
    )
    
    if class_id:
        query = query.filter_by(class_id=class_id)
    
    return query.all()


def get_schedules_optimized(class_id: Optional[int] = None, 
                          teacher_id: Optional[int] = None,
                          day_of_week: Optional[int] = None,
                          period: Optional[int] = None) -> List[Schedule]:
    """
    优化的课表查询，使用joinedload避免N+1查询
    
    Args:
        class_id: 班级ID
        teacher_id: 教师ID
        day_of_week: 星期几
        period: 第几节课
        
    Returns:
        List[Schedule]: 课表列表
    """
    query = Schedule.query.options(
        joinedload(Schedule.subject),
        joinedload(Schedule.teacher),
        joinedload(Schedule.class_obj)
    )
    
    if class_id:
        query = query.filter_by(class_id=class_id)
    if teacher_id:
        query = query.filter_by(teacher_id=teacher_id)
    if day_of_week:
        query = query.filter_by(day_of_week=day_of_week)
    if period:
        query = query.filter_by(period=period)
    
    return query.all()


def validate_hours_per_week(hours: int) -> bool:
    """
    验证周课时数是否合理
    
    Args:
        hours: 周课时数
        
    Returns:
        bool: 是否有效
    """
    return 1 <= hours <= 20


def validate_period_range(period: int, max_periods: int = 8) -> bool:
    """
    验证节次是否在有效范围内
    
    Args:
        period: 节次
        max_periods: 最大节次数
        
    Returns:
        bool: 是否有效
    """
    return 1 <= period <= max_periods


def validate_day_of_week(day: int) -> bool:
    """
    验证星期几是否有效
    
    Args:
        day: 星期几 (1-7)
        
    Returns:
        bool: 是否有效
    """
    return 1 <= day <= 7


def format_week_type(week_type: str) -> str:
    """
    格式化周类型显示
    
    Args:
        week_type: 周类型 ('all', 's', 'd', 'f')
        
    Returns:
        str: 格式化后的显示文本
    """
    week_type_map = {
        'all': '每周',
        's': '单周',
        'd': '双周',
        'f': '随机'
    }
    return week_type_map.get(week_type, '未知')


def safe_int_convert(value: Any, default: int = 0) -> int:
    """
    安全的整数转换
    
    Args:
        value: 要转换的值
        default: 默认值
        
    Returns:
        int: 转换后的整数
    """
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def batch_calculate_class_hours(class_ids: List[int]) -> Dict[int, int]:
    """
    批量计算多个班级的总课时数
    
    Args:
        class_ids: 班级ID列表
        
    Returns:
        Dict[int, int]: 班级ID到总课时数的映射
    """
    if not class_ids:
        return {}
    
    # 批量查询所有相关的授课计划
    plans = TeachingPlan.query.filter(TeachingPlan.class_id.in_(class_ids)).all()
    
    # 按班级分组计算
    class_hours = {class_id: 0 for class_id in class_ids}
    for plan in plans:
        class_hours[plan.class_id] += plan.total_hours
    
    return class_hours


def get_teacher_schedule_conflicts(teacher_id: int, day_of_week: int, period: int, 
                                 exclude_class_id: Optional[int] = None) -> List[Schedule]:
    """
    检查教师在指定时间的课程冲突
    
    Args:
        teacher_id: 教师ID
        day_of_week: 星期几
        period: 第几节课
        exclude_class_id: 排除的班级ID（用于换课时排除源班级）
        
    Returns:
        List[Schedule]: 冲突的课程列表
    """
    query = Schedule.query.filter_by(
        teacher_id=teacher_id,
        day_of_week=day_of_week,
        period=period
    )
    
    if exclude_class_id:
        query = query.filter(Schedule.class_id != exclude_class_id)
    
    return query.all()


def get_class_schedule_conflicts(class_id: int, day_of_week: int, period: int) -> List[Schedule]:
    """
    检查班级在指定时间的课程冲突
    
    Args:
        class_id: 班级ID
        day_of_week: 星期几
        period: 第几节课
        
    Returns:
        List[Schedule]: 冲突的课程列表
    """
    return Schedule.query.filter_by(
        class_id=class_id,
        day_of_week=day_of_week,
        period=period
    ).all() 