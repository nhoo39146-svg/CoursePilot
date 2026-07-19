import json
from pathlib import Path
from datetime import datetime

# ==========================
# 文件路径
# ==========================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
COURSES_PATH = DATA_DIR / "courses.json"
CONFIG_PATH = DATA_DIR / "config.json"

# ==========================
# 读取课程
# ==========================
def load_courses():
    if not COURSES_PATH.exists():
        return []
    with open(COURSES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# ==========================
# 保存课程
# ==========================
def save_courses(courses):
    with open(COURSES_PATH, "w", encoding="utf-8") as f:
        json.dump(
            courses,
            f,
            ensure_ascii=False,
            indent=4
        )

# ==========================
# 读取系统配置
# ==========================
def load_config():
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# ==========================
# 保存系统配置
# ==========================
def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(
            config,
            f,
            ensure_ascii=False,
            indent=4
        )

# ==========================
# 获取当前教学周
# ==========================
def get_current_week():
    config = load_config()
    start = datetime.strptime(
        config["semester_start"],
        "%Y-%m-%d"
    )
    today = datetime.today()
    week = (today - start).days // 7 + 1
    return max(1, week)

# ==========================
# 查找课程
# ==========================
def find_course(name):
    courses = load_courses()
    for course in courses:
        if course["name"] == name:
            return course
    return None

# ==========================
# 添加课程
# ==========================
def add_course(course):
    courses = load_courses()
    course["id"] = len(courses) + 1
    courses.append(course)
    save_courses(courses)

# ==========================
# 删除课程
# ==========================
def delete_course(course_id):
    courses = load_courses()
    courses = [
        c
        for c in courses
        if c["id"] != course_id
    ]
    # 重新编号
    for i, c in enumerate(courses):
        c["id"] = i + 1
    save_courses(courses)

# ==========================
# 修改课程
# ==========================
def update_course(course_id, new_data):
    courses = load_courses()
    for course in courses:
        if course["id"] == course_id:
            course.update(new_data)
            break
    save_courses(courses)

# ==========================
# 获取课程进度
# ==========================
def get_course_progress(course):
    current_week = get_current_week()
    week_list = course["week_list"]
    finished = len(
        [
            w
            for w in week_list
            if w < current_week
        ]
    )
    total = len(week_list)
    remain = total - finished
    percent = finished / total * 100
    return {
        "finished": finished,
        "remain": remain,
        "total": total,
        "percent": round(percent, 1)
    }

# ==========================
# 获取全部课程进度
# ==========================
def get_all_progress():
    result = []
    courses = load_courses()
    for course in courses:
        p = get_course_progress(course)
        result.append({
            "课程": course["name"],
            "已完成": p["finished"],
            "剩余": p["remain"],
            "完成率": p["percent"]
        })
    return result

# =========================
#获取当前日期/日期选择
# =========================
from datetime import datetime, date

def get_today_date_obj():
    """获取系统今日 date 对象"""
    return date.today()

def str_to_date(date_str: str):
    """字符串 YYYY-MM-DD 转 date 对象，格式错误抛出提示"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None

def date_to_str(d: date):
    """date 对象转 YYYY-MM-DD 字符串"""
    return d.strftime("%Y-%m-%d")

def calc_week_by_target_date(start_date_str: str, target_date: date):
    """
    根据开学日期 + 目标选定日期，计算对应教学周
    :param start_date_str: config中的semester_start字符串
    :param target_date: 用户选择的日期对象
    :return: 教学周数字
    """
    start = str_to_date(start_date_str)
    if not start:
        return -1
    diff_days = (target_date - start).days
    if diff_days < 0:
        return 0  # 学期未开始
    return diff_days // 7 + 1

# ==========================
# 调试
# ==========================
if __name__ == "__main__":
    courses = load_courses()
    print("课程数量：", len(courses))
    print()
    for item in get_all_progress():
        print(item)