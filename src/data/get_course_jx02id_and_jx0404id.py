import os
import json
from src.utils.session_manager import get_session
import logging


def find_course_jx02id_and_jx0404id(course, course_data):
    """在课程数据中查找课程的jx02id和jx0404id"""
    try:
        week_day_dict = {
            "1": "星期一",
            "2": "星期二",
            "3": "星期三",
            "4": "星期四",
            "5": "星期五",
            "6": "星期六",
            "7": "星期日",
        }

        # 构建搜索条件
        target_week_day = week_day_dict[course["week_day"]]
        target_week = int(course["week"])

        # 处理节次范围
        period_range = course["class_period"].rstrip("-").split("-")
        start_period = int(period_range[0])
        end_period = int(period_range[1])
        target_periods = set(range(start_period, end_period + 1))

        matching_courses = []  # 存储所有匹配的课程

        for course_item in course_data:
            if not isinstance(course_item, dict):
                continue

            # 1. 检查课程号或课程名称
            course_match = (
                course_item.get("kch") == course["course_id_or_name"]
                or course_item.get("kcmc") == course["course_id_or_name"]
            )

            # 2. 检查教师姓名
            teacher_match = course_item.get("skls") == course["teacher_name"]

            # 3. 检查上课时间（星期和节次）
            course_time = course_item.get("sksj", "")

            # 处理在线课程的特殊情况
            if course_time.strip() in ["&nbsp;", ""]:
                # 如果是在线课程，只要课程名称和教师匹配就认为找到了
                if course_match and teacher_match:
                    return {
                        "jx02id": course_item.get("jx02id"),
                        "jx0404id": course_item.get("jx0404id"),
                    }
                continue

            if not (course_match and teacher_match and target_week_day in course_time):
                continue

            # 提取并检查周次
            weeks_str = course_time.split("周")[0].strip()
            weeks = set()
            for week_range in weeks_str.split(","):
                if "-" in week_range:
                    start, end = map(int, week_range.split("-"))
                    weeks.update(range(start, end + 1))
                else:
                    weeks.add(int(week_range))

            # 检查目标周次是否在课程的周次范围内
            if target_week not in weeks:
                continue

            # 提取实际课程节次
            time_parts = course_time.split()
            found_match = False

            # 遍历每个时间段
            i = 0
            while i < len(time_parts):
                part = time_parts[i]
                # 如果找到包含"节"的部分
                if "节" in part:
                    actual_periods = part.split("节")[0]
                    if "-" in actual_periods:
                        actual_start, actual_end = map(int, actual_periods.split("-"))
                        actual_period_set = set(range(actual_start, actual_end + 1))
                        # 检查是否有重叠的节次
                        if target_periods & actual_period_set:
                            found_match = True
                            break
                i += 1

            if found_match:
                matching_courses.append(
                    {
                        "jx02id": course_item.get("jx02id"),
                        "jx0404id": course_item.get("jx0404id"),
                        "weeks": weeks,  # 保存周次信息用于后续筛选
                        "course_time": course_time,  # 保存完整的课程时间信息用于日志
                    }
                )

        # 如果找到多个匹配的课程，选择周次范围最接近的那个
        if matching_courses:
            if len(matching_courses) > 1:
                # 记录找到多个匹配课程的情况
                logging.info(f"找到多个匹配的课程:")
                for idx, mc in enumerate(matching_courses, 1):
                    logging.info(f"课程{idx}: {mc['course_time']}")

                # 选择包含目标周次且周次范围最小的课程
                best_match = min(
                    matching_courses, key=lambda x: len(x["weeks"])
                )  # 选择周次范围最小的
                logging.info(f"选择周次范围最小的课程: {best_match['course_time']}")

                return {
                    "jx02id": best_match["jx02id"],
                    "jx0404id": best_match["jx0404id"],
                }
            else:
                # 只有一个匹配的课程
                return {
                    "jx02id": matching_courses[0]["jx02id"],
                    "jx0404id": matching_courses[0]["jx0404id"],
                }

        return None

    except Exception as e:
        logging.error(f"查找课程jx02id和jx0404id时发生错误: {str(e)}")
        return None


def get_course_jx02id_and_jx0404id_by_api(course):
    """通过教务系统API获取课程的jx02id和jx0404id"""
    try:
        # 依次从专业内跨年级选课、本学期计划选课、选修选课、公选课选课、计划外选课、辅修选课搜索课程
        result = get_course_jx02id_and_jx0404id_xsxkKnjxk_by_api(course)
        if result:
            result = find_course_jx02id_and_jx0404id(course, result["aaData"])
            if result:
                return result

        result = get_course_jx02id_and_jx0404id_xsxkBxqjhxk_by_api(course)
        if result:
            result = find_course_jx02id_and_jx0404id(course, result["aaData"])
            if result:
                return result

        result = get_course_jx02id_and_jx0404id_xsxkXxxk_by_api(course)
        if result:
            result = find_course_jx02id_and_jx0404id(course, result["aaData"])
            if result:
                return result

        result = get_course_jx02id_and_jx0404id_xsxkGgxxkxk_by_api(course)
        if result:
            result = find_course_jx02id_and_jx0404id(course, result["aaData"])
            if result:
                return result

        result = get_course_jx02id_and_jx0404id_xsxkFawxk_by_api(course)
        if result:
            result = find_course_jx02id_and_jx0404id(course, result["aaData"])
            if result:
                return result
    except Exception as e:
        logging.error(f"获取课程的jx02id和jx0404id失败: {e}")
        return None


def get_course_jx02id_and_jx0404id(course):
    """通过API获取课程的jx02id和jx0404id"""
    try:
        result = get_course_jx02id_and_jx0404id_by_api(course)
        if result:
            logging.critical(
                f"通过API找到课程: 【{course['course_id_or_name']}】的 jx02id：{result['jx02id']} 和 jx0404id：{result['jx0404id']}"
            )
            return result

        logging.warning(
            f"未能找到课程: {course['course_id_or_name']}的jx02id和jx0404id"
        )
        return None
    except Exception as e:
        logging.error(f"获取课程jx02id和jx0404id时发生错误: {str(e)}")
        return None


def get_course_jx02id_and_jx0404id_xsxkGgxxkxk_by_api(course):
    """通过教务系统API获取公选课课程的jx02id和jx0404id"""
    try:
        session = get_session()
        course_id = course["course_id_or_name"]
        teacher_name = course["teacher_name"]
        class_period = course["class_period"]
        week_day = course["week_day"]

        # 选修选课页面
        response = session.get(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInXxxk",
        )
        logging.info(f"获取公选选课页面响应值: {response.status_code}")

        # 请求选课列表数据
        response = session.post(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkGgxxkxk",
            params={
                "kcxx": course_id,  # 课程名称
                "skls": teacher_name,  # 教师姓名
                "skxq": week_day,  # 上课星期
                "skjc": class_period,  # 上课节次
                "sfym": "false",  # 是否已满
                "sfct": "false",  # 是否冲突
                "sfxx": "false",  # 是否限选
            },
            data={
                "sEcho": 1,
                "iColumns": 13,
                "sColumns": "",
                "iDisplayStart": 0,
                "iDisplayLength": 15,
                "mDataProp_0": "kch",
                "mDataProp_1": "kcmc",
                "mDataProp_2": "fzmc",
                "mDataProp_3": "ktmc",
                "mDataProp_4": "xf",
                "mDataProp_5": "skls",
                "mDataProp_6": "sksj",
                "mDataProp_7": "skdd",
                "mDataProp_8": "xqmc",
                "mDataProp_9": "ctsm",
                "mDataProp_10": "czOper",
            },
        )

        logging.info(f"获取公选选课列表数据响应值: {response.status_code}")
        response_data = json.loads(response.text)

        # 检查aaData是否为空
        if not response_data.get("aaData"):
            logging.warning("API返回的aaData为空")
            return None

        return response_data
    except Exception as e:
        logging.error(f"获取公选选课的jx02id和jx0404id失败: {e}")
        return None


def get_course_jx02id_and_jx0404id_xsxkXxxk_by_api(course):
    """通过教务系统API获取选修课课程的jx02id和jx0404id"""
    try:
        session = get_session()
        course_id = course["course_id_or_name"]
        teacher_name = course["teacher_name"]
        class_period = course["class_period"]
        week_day = course["week_day"]

        # 选修选课页面
        response = session.get(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInXxxk",
        )
        logging.info(f"获取选修选课页面响应值: {response.status_code}")

        # 请求选课列表数据
        response = session.post(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkXxxk",
            params={
                "kcxx": course_id,  # 课程名称
                "skls": teacher_name,  # 教师姓名
                "skxq": week_day,  # 上课星期
                "skjc": class_period,  # 上课节次
                "sfym": "false",  # 是否已满
                "sfct": "false",  # 是否冲突
                "sfxx": "false",  # 是否限选
            },
            data={
                "sEcho": 1,
                "iColumns": 11,
                "sColumns": "",
                "iDisplayStart": 0,
                "iDisplayLength": 15,
                "mDataProp_0": "kch",
                "mDataProp_1": "kcmc",
                "mDataProp_2": "fzmc",
                "mDataProp_3": "ktmc",
                "mDataProp_4": "xf",
                "mDataProp_5": "skls",
                "mDataProp_6": "sksj",
                "mDataProp_7": "skdd",
                "mDataProp_8": "xqmc",
                "mDataProp_9": "ctsm",
                "mDataProp_10": "czOper",
            },
        )

        logging.info(f"获取选修选课列表数据响应值: {response.status_code}")
        response_data = json.loads(response.text)

        # 检查aaData是否为空
        if not response_data.get("aaData"):
            logging.warning("API返回的aaData为空")
            return None

        return response_data
    except Exception as e:
        logging.error(f"获取选修选课的jx02id和jx0404id失败: {e}")
        return None


def get_course_jx02id_and_jx0404id_xsxkBxqjhxk_by_api(course):
    """通过教务系统API获取本学期计划选课课程的jx02id和jx0404id"""
    try:
        session = get_session()
        course_id = course["course_id_or_name"]
        teacher_name = course["teacher_name"]
        class_period = course["class_period"]
        week_day = course["week_day"]

        # 选修选课页面
        response = session.get(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInBxqjhxk",
        )
        logging.info(f"获取本学期计划选课页面响应值: {response.status_code}")

        # 请求选课列表数据
        response = session.post(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkBxqjhxk",
            params={
                "kcxx": course_id,  # 课程名称
                "skls": teacher_name,  # 教师姓名
                "skxq": week_day,  # 上课星期
                "skjc": class_period,  # 上课节次
                "sfym": "false",  # 是否已满
                "sfct": "false",  # 是否冲突
                "sfxx": "false",  # 是否限选
            },
            data={
                "sEcho": 1,
                "iColumns": 12,
                "sColumns": "",
                "iDisplayStart": 0,
                "iDisplayLength": 15,
                "mDataProp_0": "kch",
                "mDataProp_1": "kcmc",
                "mDataProp_2": "fzmc",
                "mDataProp_3": "ktmc",
                "mDataProp_4": "xf",
                "mDataProp_5": "skls",
                "mDataProp_6": "sksj",
                "mDataProp_7": "skdd",
                "mDataProp_8": "xqmc",
                "mDataProp_9": "ctsm",
                "mDataProp_10": "czOper",
            },
        )

        logging.info(f"获取本学期计划选课列表数据响应值: {response.status_code}")
        response_data = json.loads(response.text)

        # 检查aaData是否为空
        if not response_data.get("aaData"):
            logging.warning("API返回的aaData为空")
            return None

        return response_data
    except Exception as e:
        logging.error(f"获取本学期计划选课的jx02id和jx0404id失败: {e}")
        return None


def get_course_jx02id_and_jx0404id_xsxkKnjxk_by_api(course):
    """通过教务系统API获取专业内跨年级选课课程的jx02id和jx0404id"""
    try:
        session = get_session()
        course_id = course["course_id_or_name"]
        teacher_name = course["teacher_name"]
        class_period = course["class_period"]
        week_day = course["week_day"]

        # 专业内跨年级选课页面
        response = session.get(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInKnjxk",
        )
        logging.info(f"获取专业内跨年级选课页面响应值: {response.status_code}")

        # 请求选课列表数据
        response = session.post(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkKnjxk",
            params={
                "kcxx": course_id,  # 课程名称
                "skls": teacher_name,  # 教师姓名
                "skxq": week_day,  # 上课星期
                "skjc": class_period,  # 上课节次
                "sfym": "false",  # 是否已满
                "sfct": "false",  # 是否冲突
                "sfxx": "false",  # 是否限选
            },
            data={
                "sEcho": 1,
                "iColumns": 12,
                "sColumns": "",
                "iDisplayStart": 0,
                "iDisplayLength": 15,
                "mDataProp_0": "kch",
                "mDataProp_1": "kcmc",
                "mDataProp_2": "fzmc",
                "mDataProp_3": "ktmc",
                "mDataProp_4": "xf",
                "mDataProp_5": "skls",
                "mDataProp_6": "sksj",
                "mDataProp_7": "skdd",
                "mDataProp_8": "xqmc",
                "mDataProp_9": "ctsm",
                "mDataProp_10": "czOper",
            },
        )

        logging.info(f"获取专业内跨年级选课列表数据响应值: {response.status_code}")

        # 新增代码：检查响应内容是否为JSON格式
        try:
            response_data = json.loads(response.text)

            # 检查aaData是否为空
            if not response_data.get("aaData"):
                logging.warning("API返回的aaData为空")
                return None

            return response_data
        except ValueError:
            logging.error("API返回的数据不是有效的JSON格式")
            return None

    except Exception as e:
        logging.error(f"获取专业内跨年级选课的jx02id和jx0404id失败: {e}")
        return None


def get_course_jx02id_and_jx0404id_xsxkFawxk_by_api(course):
    """通过教务系统API获取计划外选课课程的jx02id和jx0404id"""
    try:
        session = get_session()
        course_id = course["course_id_or_name"]
        teacher_name = course["teacher_name"]
        class_period = course["class_period"]
        week_day = course["week_day"]

        # 计划外选课页面
        response = session.get(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInFawxk",
        )
        logging.info(f"获取计划外选课页面响应值: {response.status_code}")

        # 请求选课列表数据
        response = session.post(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkFawxk",
            params={
                "kcxx": course_id,  # 课程名称
                "skls": teacher_name,  # 教师姓名
                "skxq": week_day,  # 上课星期
                "skjc": class_period,  # 上课节次
                "sfym": "false",  # 是否已满
                "sfct": "false",  # 是否冲突
                "sfxx": "false",  # 是否限选
            },
            data={
                "sEcho": 1,
                "iColumns": 12,
                "sColumns": "",
                "iDisplayStart": 0,
                "iDisplayLength": 15,
                "mDataProp_0": "kch",
                "mDataProp_1": "kcmc",
                "mDataProp_2": "fzmc",
                "mDataProp_3": "ktmc",
                "mDataProp_4": "xf",
                "mDataProp_5": "skls",
                "mDataProp_6": "sksj",
                "mDataProp_7": "skdd",
                "mDataProp_8": "xqmc",
                "mDataProp_9": "ctsm",
                "mDataProp_10": "czOper",
            },
        )

        logging.info(f"获取计划外选课列表数据响应值: {response.status_code}")
        response_data = json.loads(response.text)

        # 检查aaData是否为空
        if not response_data.get("aaData"):
            logging.warning("API返回的aaData为空")
            return None

        return response_data
    except Exception as e:
        logging.error(f"获取计划外选课的jx02id和jx0404id失败: {e}")
        return None
