import csv
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

# ==========================
# 文件路径
# ==========================

BASE_DIR = Path(__file__).parent

DATA_DIR = BASE_DIR / "data"

CSV_PATH = DATA_DIR / "course_schedule.csv"

COURSE_CONFIG_PATH = DATA_DIR / "course_config.json"

COURSES_PATH = DATA_DIR / "courses.json"

SYSTEM_CONFIG_PATH = DATA_DIR / "config.json"


# ==========================
# 创建data目录
# ==========================

DATA_DIR.mkdir(exist_ok=True)


# ==========================
# 读取JSON
# ==========================

def load_json(path):

    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ==========================
# 保存JSON
# ==========================

def save_json(path, data):

    with open(path, "w", encoding="utf-8") as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


# ==========================
# 第一次运行初始化config
# ==========================

def init_system_config():

    config = load_json(SYSTEM_CONFIG_PATH)

    if config == {}:

        config = {

            "semester_start": "",

            "semester_end": ""

        }

        save_json(SYSTEM_CONFIG_PATH, config)

    return config


# ==========================
# 解析周数字符串
# ==========================

def parse_weeks(week_string):
    """
    支持格式：

    15

    3-13

    1-9,12

    1-8,10-16

    1-16(单)

    1-16(双)

    返回：

    [1,2,3,4...]

    """

    result = []

    week_string = week_string.replace("周", "")

    is_single = "单" in week_string

    is_double = "双" in week_string

    week_string = week_string.replace("(单)", "")

    week_string = week_string.replace("(双)", "")

    week_string = week_string.replace("，", ",")

    week_string = week_string.replace("、", ",")


    parts = week_string.split(",")

    for part in parts:

        part = part.strip()

        if "-" in part:

            start, end = part.split("-")

            start = int(start)

            end = int(end)

            for i in range(start, end + 1):

                result.append(i)

        else:

            result.append(int(part))

    if is_single:

        result = [i for i in result if i % 2 == 1]

    if is_double:

        result = [i for i in result if i % 2 == 0]

    return sorted(list(set(result)))


# ==========================
# 最大教学周
# ==========================
def get_max_week(courses):
    max_week = 0
    for course in courses:
        week_list = parse_weeks(course["weeks"])
        current_max = max(week_list)
        if current_max > max_week:
            max_week = current_max
    return max_week

#============================
#重置学期开始时间
#============================

def reset_semester_start():
    """手动重置开学日期，强制弹出输入框"""
    config = init_system_config()
    new_date = input("请重新输入本学期第一周周一日期(YYYY-MM-DD)：")
    # 简单校验日期格式，防止输错
    from datetime import datetime
    try:
        datetime.strptime(new_date, "%Y-%m-%d")
    except ValueError:
        print("日期格式错误！请按照 YYYY-MM-DD 输入，例如 2026-09-22")
        return
    config["semester_start"] = new_date
    # 重新计算学期结束日期
    # 先读取现有课程
    courses = load_json(COURSES_PATH)
    if courses:
        max_week = get_max_week(courses)
        config["semester_end"] = calculate_semester_end(new_date, max_week)
    save_json(SYSTEM_CONFIG_PATH, config)
    print("开学日期修改成功！")



# ==========================
# 自动计算学期结束日期
# ==========================

def calculate_semester_end(start_date, max_week):

    start = datetime.strptime(start_date, "%Y-%m-%d")

    end = start + timedelta(weeks=max_week - 1, days=6)

    return end.strftime("%Y-%m-%d")


# ==========================
# 根据日期计算当前教学周
# ==========================

def get_current_week(start_date):

    today = datetime.today()

    start = datetime.strptime(start_date, "%Y-%m-%d")

    delta = (today - start).days

    return delta // 7 + 1


# ==========================
# 计算课程已完成次数
# ==========================

def finished_classes(course, current_week):

    week_list = parse_weeks(course["weeks"])

    count = 0

    for week in week_list:

        if week < current_week:

            count += 1

    return count


# ==========================
# 计算课程剩余次数
# ==========================

def remaining_classes(course, current_week):

    total = len(parse_weeks(course["weeks"]))

    finish = finished_classes(course, current_week)

    return total - finish
# ==========================
# 导入CSV
# ==========================

def import_csv():

    # 读取课程配置
    course_config = load_json(COURSE_CONFIG_PATH)

    # 初始化系统配置
    config = init_system_config()

    # 第一次运行输入学期开始日期
    if config["semester_start"] == "":

        config["semester_start"] = input(
            "请输入本学期第一周周一日期(YYYY-MM-DD)："
        )

    courses = []

    # 自动识别UTF-8或GBK编码
    try:
        f = open(CSV_PATH, "r", encoding="utf-8-sig")
        reader = csv.DictReader(f)
        rows = list(reader)
        f.close()

    except UnicodeDecodeError:

        f = open(CSV_PATH, "r", encoding="gbk")
        reader = csv.DictReader(f)
        rows = list(reader)
        f.close()

    course_id = 1

    for row in rows:

        name = row["课程名称"].strip()

        weeks = row["周数"].strip()

        week_list = parse_weeks(weeks)

        # 默认值
        credit = 2
        difficulty = 3

        # 如果配置文件中存在该课程
        if name in course_config:

            credit = course_config[name].get("credit", 2)

            difficulty = course_config[name].get("difficulty", 3)

        course = {

            "id": course_id,

            "name": name,

            "teacher": row["老师"],

            "classroom": row["地点"],

            "weekday": int(row["星期"]),

            "start_section": int(row["开始节数"]),

            "end_section": int(row["结束节数"]),

            "weeks": weeks,

            # 新增
            "week_list": week_list,

            "credit": credit,

            "difficulty": difficulty,

            "total_classes": len(week_list)

        }

        courses.append(course)

        course_id += 1

    # -------------------------
    # 自动计算学期结束日期
    # -------------------------

    max_week = get_max_week(courses)

    config["semester_end"] = calculate_semester_end(
        config["semester_start"],
        max_week
    )

    save_json(
        SYSTEM_CONFIG_PATH,
        config
    )

    # -------------------------
    # 保存courses.json
    # -------------------------

    save_json(
        COURSES_PATH,
        courses
    )

    print("\n========================")

    print("课表导入成功！")

    print("课程数量：", len(courses))

    print("学期开始：", config["semester_start"])

    print("学期结束：", config["semester_end"])

    print("========================")


# ==========================
# 查看课程（调试用）
# ==========================

def show_courses():

    courses = load_json(COURSES_PATH)

    print()

    for course in courses:

        print("-" * 50)

        print("课程：", course["name"])

        print("教师：", course["teacher"])

        print("地点：", course["classroom"])

        print("星期：", course["weekday"])

        print("节次：",
              course["start_section"],
              "-",
              course["end_section"])

        print("周数：", course["weeks"])

        print("课程次数：", course["total_classes"])

        print("学分：", course["credit"])

        print("难度：", course["difficulty"])


# ==========================
# 测试
# ==========================

if __name__ == "__main__":

    import_csv()

    # 查看导入结果
    show_courses()
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


# ==========================
# 调试
# ==========================

if __name__ == "__main__":

    courses = load_courses()

    print("课程数量：", len(courses))

    print()

    for item in get_all_progress():

        print(item)
