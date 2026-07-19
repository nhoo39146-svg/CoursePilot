from csv_import import import_csv
from data import load_courses, load_config
from pathlib import Path

# ========= 自动导入 =========
DATA_DIR = Path(__file__).parent / "data"
COURSES_PATH = DATA_DIR / "courses.json"

def init_system():
    if not COURSES_PATH.exists():
        print("首次运行，开始导入学校课表...\n")
        import_csv()
        print("\n初始化完成！")

# ========== 日期选择 =============
from data import get_today_date_obj, str_to_date, date_to_str

def select_target_date():
    """
    交互选择日期：1查看今日 2手动输入指定日期
    返回选中的date对象
    """
    print("\n===== 日期选择 =====")
    print("1. 使用今日系统日期查看")
    print("2. 手动输入日期查看任意一天课表/进度")
    choice = input("请选择(1/2)：").strip()

    if choice == "1":
        target = get_today_date_obj()
        print(f"已选择今日：{date_to_str(target)}")
        return target
    elif choice == "2":
        while True:
            input_day = input("请输入查询日期（格式YYYY-MM-DD）：").strip()
            target = str_to_date(input_day)
            if target is not None:
                print(f"已选择目标日期：{input_day}")
                return target
            else:
                print("日期格式错误，请重新输入，示例：2026-09-20")
    else:
        print("输入错误，默认使用今日日期")
        return get_today_date_obj()

# ========= 主菜单 =========
def show_menu():
    print("\n==============================")
    print("      CoursePilot")
    print("==============================")
    print("1. 查看课程")
    print("2. 课程管理（A）")
    print("3. 学期统计（B）")
    print("4. 智能推荐（C）")
    print("5. 数据可视化（D）")
    print("6. 重置学期开学日期")
    print("0. 退出")
    print("==============================")

# ========= 查看课程 =========
def show_courses():
    courses = load_courses()
    print("\n当前课程：\n")
    for c in courses:
        print(f"{c['id']}. {c['name']}")
        print(f"教师：{c['teacher']}")
        print(f"地点：{c['classroom']}")
        print(f"星期：{c['weekday']}")
        print(f"节次：{c['start_section']}-{c['end_section']}")
        print(f"周数：{c['weeks']}")
        print(f"学分：{c['credit']}")
        print(f"难度：{c['difficulty']}")
        print("-" * 40)

# ========= 主程序 =========
def main():
    init_system()
    config = load_config()
    print("\n学期开始：", config["semester_start"])
    print("学期结束：", config["semester_end"])

    # 把兼容导入判断放进main内部，运行时再检测，不提前阻塞
    b_enable = True
    c_enable = True
    d_enable = True
    try:
        from modules.statistics import get_all_course_progress
        from modules.recommend import get_recommend_schedule
        from modules.visualize import draw_course_progress_bar, draw_recommend_rank_bar
    except ImportError:
        b_enable = False
        c_enable = False
        d_enable = False
        print("\n提示：统计/推荐/可视化模块尚未开发完成，对应3/4/5功能暂时不可用\n")

    while True:
        show_menu()
        choice = input("请选择：")
        if choice == "1":
            show_courses()

        elif choice == "2":
            print("\n>>> 请运行 modules/course.py")

        elif choice == "3":
            # 无论模块是否完成，都会先弹出日期选择
            select_target_date()
            if not b_enable:
                print("B模块（学期统计）暂未开发完成！")
            else:
                target_day = select_target_date()
                progress_info = get_all_course_progress(target_day)
                print(f"\n===== 学期统计 | 查询日期：{progress_info['target_query_date']} =====")
                print(f"当前教学周：{progress_info['current_week']}")
                print(f"距离期末剩余天数：{progress_info['semester_remain_days']}")
                print(f"剩余周末总数：{progress_info['remain_weekend_count']}\n")
                course_list = progress_info["course_list"]
                if not course_list:
                    print("暂无课程统计数据")
                else:
                    for item in course_list:
                        print(f"{item['course_name']} | 总课时：{item['total_classes']} | 已上：{item['finished']} | 剩余：{item['remain']} | 完成率：{item['percent']}%")

        elif choice == "4":
            # 无论模块是否完成，都会先弹出日期选择
            select_target_date()
            if not c_enable:
                print("C模块（智能推荐）暂未开发完成！")
            else:
                target_day = select_target_date()
                progress_info = get_all_course_progress(target_day)
                recommend_list = get_recommend_schedule(progress_info)
                print("\n===== 复习优先级推荐（分数越高，优先复习）=====")
                if not recommend_list:
                    print("暂无课程，无法生成推荐列表")
                else:
                    for sort_num, data in enumerate(recommend_list, start=1):
                        print(f"第{sort_num}优先级：{data['course_name']} 优先级分数：{data['priority_score']}")

        elif choice == "5":
            # 无论模块是否完成，都会先弹出日期选择
            select_target_date()
            if not d_enable:
                print("D模块（可视化）暂未开发完成！")
            else:
                target_day = select_target_date()
                progress_info = get_all_course_progress(target_day)
                recommend_list = get_recommend_schedule(progress_info)
                print("\n===== 课程课时进度可视化 =====")
                draw_course_progress_bar(progress_info)
                print("\n===== 复习优先级次序可视化 =====")
                draw_recommend_rank_bar(recommend_list)

        elif choice == "6":
            from csv_import import reset_semester_start
            reset_semester_start()

        elif choice == "0":
            print("\n感谢使用 CoursePilot！")
            break
        else:
            print("\n输入有误，请重新输入。")

if __name__ == "__main__":
    main()