import json
from datetime import datetime, timedelta

COURSE_JSON_PATH = "data/courses.json"
CONFIG_JSON_PATH = "data/config.json"

def load_config():
    """读取学期开学、结束日期配置"""
    with open(CONFIG_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_courses():
    """读取所有课程信息"""
    with open(COURSE_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def is_weekend(date: datetime) -> bool:
    """判断某天是否周六/周日"""
    return date.weekday() >= 5

def date_str_to_datetime(date_str: str) -> datetime:
    """把字符串日期 yyyy-MM-dd 转成日期对象"""
    return datetime.strptime(date_str, "%Y-%m-%d")

def calc_course_class_times(course: dict, start_date: datetime, end_date: datetime, now_date: datetime):
    """计算单门课：已上次数、剩余次数、剩余课时"""
    course_id = course.get("course_id", 0)
    course_name = course.get("course_name", "未知课程")
    course_weeks = set(course.get("weeks", []))
    single_hour = course.get("single_hour", 4)

    total_class_times = len(course_weeks)

    past_times = 0
    delta_days = (now_date - start_date).days
    for day_offset in range(delta_days + 1):
        current_day = start_date + timedelta(days=day_offset)
        week_num = (day_offset // 7) + 1
        if week_num in course_weeks:
            past_times += 1

    remain_times = total_class_times - past_times
    remain_hour = remain_times * single_hour
    return {
        "course_id": course_id,
        "course_name": course_name,
        "finished_times": past_times,
        "remain_times": remain_times,
        "remain_class_hour": remain_hour
    }

def get_semester_total_stat(start_date: datetime, end_date: datetime, now_date: datetime):
    """全局学期统计：总天数、已过天数、剩余天数、剩余周末"""
    total_days = (end_date - start_date).days + 1
    past_days = (now_date - start_date).days + 1
    if past_days < 0:
        past_days = 0
    remain_days = (end_date - now_date).days
    if remain_days < 0:
        remain_days = 0

    total_weekend = 0
    remain_weekend = 0
    for day_offset in range(total_days):
        day = start_date + timedelta(days=day_offset)
        if is_weekend(day):
            total_weekend += 1
            if day > now_date:
                remain_weekend += 1

    return {
        "total_days": total_days,
        "past_days": past_days,
        "remain_days": remain_days,
        "total_weekend": total_weekend,
        "remain_weekend": remain_weekend
    }

def get_all_semester_stat(current_date_str: str):
    """对外统一入口函数，main.py直接调用这个"""
    config = load_config()
    courses = load_courses()
    start_str = config["semester_start"]
    end_str = config["semester_end"]

    start_date = date_str_to_datetime(start_str)
    end_date = date_str_to_datetime(end_str)
    now_date = date_str_to_datetime(current_date_str)

    semester_total = get_semester_total_stat(start_date, end_date, now_date)
    course_list = []
    for course in courses:
        course_stat = calc_course_class_times(course, start_date, end_date, now_date)
        course_list.append(course_stat)

    result = {
        "semester_total": semester_total,
        "course_list": course_list
    }
    return result

# 本地测试代码
if __name__ == "__main__":
    test_date = "2026-07-20"
    output = get_all_semester_stat(test_date)
    print(json.dumps(output, ensure_ascii=False, indent=2))