# CoursePilot 开发贡献规范
## 一、模块对外统一接口规范
### 模块B statistics
函数：get_all_course_progress(target_date)
入参：date 对象
返回结构：{target_query_date, current_week, semester_remain_days, remain_weekend_count, course_list}

示例：
{
    "target_query_date": "2026-10-20",  # 查询日期字符串 YYYY-MM-DD
    "current_week": 8,                  # 当前查询教学周
    "semester_remain_days": 86,         # 距离期末总剩余天数
    "remain_weekend_count": 22,         # 剩余周末天数
    "course_list": [                    # 所有课程进度数组（核心输出，供C/D使用）
        {
            "course_name": "高等数学",
            "credit": 4,                # 学分（给C算权重）
            "difficulty": 5,           # 难度1-5（给C算权重）
            "total_classes": 16,
            "finished": 7,
            "remain": 9,
            "percent": 43.8
        },
        {
            "course_name": "Python程序设计",
            "credit": 3,
            "difficulty": 4,
            "total_classes": 14,
            "finished": 6,
            "remain": 8,
            "percent": 42.9
        }
    ]
}

### 模块C recommend
函数：get_recommend_schedule(progress_data)
入参：B模块完整返回字典  
返回结构：按优先级降序的复习清单数组

示例：
[
    {
        "course_name": "高等数学",
        "priority_score": 35
    },
    {
        "course_name": "Python程序设计",
        "priority_score": 28
    },
    {
        "course_name": "大学英语",
        "priority_score": 12
    }
]

### 模块D visualize
1. draw_course_progress_bar(progress_data)
2. draw_recommend_rank_bar(recommend_list)

示例：
===== 复习优先级排序（分数越高越优先）=====
★★★★★ 高等数学 | 优先级分数：35
★★★☆☆ Python程序设计 | 优先级分数：28
★☆☆☆☆ 大学英语 | 优先级分数：12

## 二、全局数据结构规范
1. courses.json 单课程字段约束
2. config.json 配置字段约束

## 三、分支管理
main 保护分支，仅PR合并；功能分支 feature/module-xx