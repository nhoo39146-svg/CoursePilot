from typing import List, Dict

# ====================== 权重配置常量（可调整） ======================
WEIGHT_CREDIT = 2.5      # 学分权重
WEIGHT_DIFFICULTY = 3.0  # 难度权重
WEIGHT_REMAIN = 1.8      # 剩余课时权重
# 单课时预估复习时长（单位：小时）
HOUR_PER_CLASS = 1.2
# ==================================================================

def get_recommend_schedule(progress_data: Dict) -> List[Dict]:
    """
    模块C统一对外接口：生成课程复习优先级清单
    :param progress_data: 模块B get_all_course_progress 返回的完整字典
    :return: 按优先级降序的复习清单数组，格式匹配CONTRIBUTING.md规范
    """
    course_list = progress_data.get("course_list", [])
    recommend_result = []

    for course in course_list:
        # 提取课程基础维度数据
        course_name = course["course_name"]
        credit = course["credit"]
        difficulty = course["difficulty"]
        remain_classes = course["remain"]
        total_classes = course["total_classes"]
        finished = course["finished"]
        percent = course["percent"]

        # 优先级分数计算逻辑
        # 若课程已全部上完，优先级置0
        if remain_classes <= 0:
            priority_score = 0.0
            estimate_hour = 0.0
        else:
            # 三维加权综合得分
            base_score = (
                credit * WEIGHT_CREDIT
                + difficulty * WEIGHT_DIFFICULTY
                + remain_classes * WEIGHT_REMAIN
            )
            # 进度衰减系数：完成率越低，加权放大优先级
            progress_factor = 1 + ((100 - percent) / 100)
            priority_score = round(base_score * progress_factor, 1)
            # 预估总复习时长
            estimate_hour = round(remain_classes * HOUR_PER_CLASS, 1)

        item = {
            "course_name": course_name,
            "priority_score": priority_score,
            "credit": credit,
            "difficulty": difficulty,
            "remain_classes": remain_classes,
            "total_classes": total_classes,
            "finished_classes": finished,
            "complete_percent": percent,
            "estimate_review_hour": estimate_hour
        }
        recommend_result.append(item)

    # 按优先级分数降序排序，同分按剩余课时降序
    recommend_result.sort(key=lambda x: (x["priority_score"], x["remain_classes"]), reverse=True)
    return recommend_result


# ====================== 辅助工具函数（可选调用） ======================
def filter_unfinished_courses(recommend_list: List[Dict]) -> List[Dict]:
    """过滤掉已全部结课的课程，只保留需要复习的课程"""
    return [item for item in recommend_list if item["priority_score"] > 0]


def get_top_n_recommend(recommend_list: List[Dict], top_n: int = 5) -> List[Dict]:
    """获取前N门最高优先级课程"""
    unfinished = filter_unfinished_courses(recommend_list)
    return unfinished[:top_n]


# ====================== 本地调试入口 ======================
if __name__ == "__main__":
    # 模拟模块B输出的标准测试数据（与CONTRIBUTING.md示例结构一致）
    mock_b_data = {
        "target_query_date": "2026-10-20",
        "current_week": 8,
        "semester_remain_days": 86,
        "remain_weekend_count": 22,
        "course_list": [
            {
                "course_name": "高等数学",
                "credit": 5,
                "difficulty": 5,
                "total_classes": 15,
                "finished": 7,
                "remain": 8,
                "percent": 46.7
            },
            {
                "course_name": "程序设计基础(Python)A",
                "credit": 3,
                "difficulty": 4,
                "total_classes": 11,
                "finished": 6,
                "remain": 5,
                "percent": 54.5
            },
            {
                "course_name": "基础英语A",
                "credit": 4,
                "difficulty": 3,
                "total_classes": 15,
                "finished": 10,
                "remain": 5,
                "percent": 66.7
            },
            {
                "course_name": "军事理论",
                "credit": 2,
                "difficulty": 3,
                "total_classes": 2,
                "finished": 2,
                "remain": 0,
                "percent": 100.0
            }
        ]
    }

    # 调用核心推荐函数
    rec_list = get_recommend_schedule(mock_b_data)
    print("===== 完整复习优先级清单 =====")
    for item in rec_list:
        print(f"课程：{item['course_name']:20} | 优先级分数：{item['priority_score']:5.1f} | 预估复习时长：{item['estimate_review_hour']}h")

    print("\n===== Top3 优先复习课程 =====")
    top3 = get_top_n_recommend(rec_list, 3)
    for idx, item in enumerate(top3, start=1):
        print(f"{idx}. {item['course_name']}  分数：{item['priority_score']}")