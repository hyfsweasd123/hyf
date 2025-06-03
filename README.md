# 中学排课系统

基于 Flask 开发的中学排课系统，支持教师管理、班级管理、学科管理、合班设置、授课计划管理以及自动排课和手动排课功能。

## 主要功能

### 基础数据管理
- 基本设置
- 教师管理（支持导入、导出）
- 学科管理（支持导入、导出）
- 授课计划管理
- 合班设置
- 班级管理（支持导入、导出）

### 排课管理
- 排课设置
- 自动排课
- 手动排课
- 课表查看
- 课表调整

### 用户管理
- 管理员账户（拥有全部权限）
- 子管理员账户（不可修改课表，但可查看和导出课表，以及代课安排）

## 技术栈

- 后端：Flask、SQLAlchemy、Python
- 前端：HTML、CSS、JavaScript、Bootstrap 5
- 数据库：SQLite

## 安装和使用

### 环境要求

- Python 3.8+
- pip

### 安装步骤

1. 克隆仓库：
   ```
   git clone https://github.com/yourusername/school-schedule-system.git
   cd school-schedule-system
   ```

2. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

3. 初始化数据库：
   ```
   flask init-db
   ```

4. 运行应用：
   ```
   flask run
   ```

5. 访问系统：
   打开浏览器，访问 http://localhost:5000

### 默认账户

- 管理员账户：
  - 用户名：admin
  - 密码：admin123

## 使用流程

1. 登录系统
2. 添加基础数据：教师、学科、班级等
3. 创建合班设置（如有需要）
4. 配置授课计划
5. 调整排课设置
6. 使用自动排课或者手动排课生成课表
7. 查看和导出课表

## 系统截图

(项目截图将在此处展示)

## 数据导入格式

### 教师数据导入

支持 CSV 和 Excel 格式，必填列包括：
- name：教师姓名
- gender：性别
- staff_id：教师工号

可选列：
- phone：电话号码
- email：电子邮箱
- max_hours_per_day：每天最大授课时数
- max_hours_per_week：每周最大授课时数
- subjects：教授学科（逗号分隔的学科代码）

### 学科数据导入

支持 CSV 和 Excel 格式，必填列包括：
- name：学科名称
- code：学科代码

可选列：
- is_major：是否主科（1表示是，0表示否）

### 班级数据导入

支持 CSV 和 Excel 格式，必填列包括：
- name：班级名称
- grade：年级
- class_number：班号

可选列：
- head_teacher_staff_id：班主任工号
- student_count：学生人数

## 许可证

MIT License

## 贡献

欢迎提交问题和功能请求。 