import json

# 进度条填充字符
FILL_CHAR = "█"
EMPTY_CHAR = "─"
BAR_LENGTH = 30  # 统一进度条长度

def load_json(file_path: str) -> dict:
    """通用读取json工具函数，复用项目规范"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def draw_term_progress(total_days: int, used_days: int) -> None:
    """
    绘制【学期整体进度条】
    :param total_days: 学期总天数
    :param used_days: 已过去在校天数
    """
    if total_days <= 0:
        print("学期进度：暂无学期数据")
        return
    progress = used_days / total_days
    fill_num = int(BAR_LENGTH * progress)
    empty_num = BAR_LENGTH - fill_num
    bar = FILL_CHAR * fill_num + EMPTY_CHAR * empty_num
    percent = round(progress * 100, 1)
    print(f"\n===== 学期整体进度 [{percent}%] =====")
    print(f"[{bar}] 已过{used_days}天 / 总计{total_days}天")


def draw_course_progress(course_list: list) -> None:
    """
    批量绘制【单门课程课时进度条】
    :param course_list: B模块输出课程统计列表，格式：
        [{"name":"课程名", "finished":已上课时, "total":总课时}, ...]
    """
    print("\n===== 各门课程课时进度 =====")
    for course in course_list:
        name = course["name"]
        finished = course["finished"]
        total = course["total"]
        if total <= 0:
            print(f"{name:10s} | 无课时数据")
            continue
        progress = finished / total
        fill_num = int(BAR_LENGTH * progress)
        empty_num = BAR_LENGTH - fill_num
        bar = FILL_CHAR * fill_num + EMPTY_CHAR * empty_num
        percent = round(progress * 100, 1)
        print(f"{name:10s} | [{bar}] {finished}/{total} 课时 ({percent}%)")


def draw_recommend_priority(recommend_list: list) -> None:
    """
    绘制【复习优先级可视化条】，分数越高进度条越长
    :param recommend_list: C模块输出推荐列表，格式：
        [{"name":"课程名", "score":综合复习分数, "study_hour":预估时长}, ...]
    """
    if not recommend_list:
        print("\n===== 复习优先级推荐 =====")
        print("暂无待复习课程")
        return
    # 获取最大分数做比例基准
    max_score = max(item["score"] for item in recommend_list)
    print("\n===== 复习优先级排序（分数越高优先复习） =====")
    for idx, item in enumerate(recommend_list, start=1):
        name = item["name"]
        score = item["score"]
        hour = item["study_hour"]
        # 按分数占最大值比例绘制条
        ratio = score / max_score if max_score != 0 else 0
        fill_num = int(BAR_LENGTH * ratio)
        empty_num = BAR_LENGTH - fill_num
        bar = FILL_CHAR * fill_num + EMPTY_CHAR * empty_num
        print(f"第{idx:2d}位 {name:10s} | [{bar}] 综合分:{score:.1f} | 预估复习{hour}h")


def show_all_visual(stat_data: dict, recommend_data: list) -> None:
    """
    对外统一调用入口，main.py直接调用此函数即可
    :param stat_data: B模块统计输出，包含term_total、term_used、courses
    :param recommend_data: C模块推荐排序列表
    """
    # 1. 绘制学期总进度
    draw_term_progress(
        total_days=stat_data.get("term_total_days", 0),
        used_days=stat_data.get("term_used_days", 0)
    )
    # 2. 绘制每门课程课时进度
    draw_course_progress(course_list=stat_data.get("course_stats", []))
    # 3. 绘制复习优先级图表
    draw_recommend_priority(recommend_list=recommend_data)


# 测试入口（本地调试用，提交不影响main）
if __name__ == "__main__":
    # 模拟B模块统计输出数据
    mock_stat = {
        "term_total_days": 120,
        "term_used_days": 45,
        "course_stats": [
            {"name": "高等数学", "finished": 12, "total": 32},
            {"name": "Python编程", "finished": 20, "total": 32},
            {"name": "大学英语", "finished": 8, "total": 30}
        ]
    }
    # 模拟C模块推荐优先级数据
    mock_recommend = [
        {"name": "高等数学", "score": 92.5, "study_hour": 8},
        {"name": "大学英语", "score": 76.2, "study_hour": 5},
        {"name": "Python编程", "score": 43.1, "study_hour": 3}
    ]
    # 执行可视化输出
    show_all_visual(mock_stat, mock_recommend)