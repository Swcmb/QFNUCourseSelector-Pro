# QFNUCourseSelector

QFNU 抢课脚本

## 仍在开发者，目前只能抢公选课

## 如何使用

### git clone

```bash
git clone git@github.com:W1ndys/QFNUCourseSelector.git
```

### 安装依赖

双击`create_venv_windows.bat`，等待安装完成

### 运行脚本

双击`run_app_in_venv_windows.bat`，等待运行完成，生成配置文件`config.json`

### 配置文件

配置文件`config.json`，格式如下：

```json
{
  "user_account": "你的学号",
  "user_password": "你的密码",
  "select_semester": "你的选课学期，例如：2024-2025-2学期2021级选课",
  "course": [
    {
      "course_id": "课程id",
      "teacher_name": "教师名称",
      "week_day": "上课星期", // 填(1,2,3,4,5,6,7)
      "class_period": "上课节次", // 填(1-2-,3-4-,5-6-,7-8-,9-10-11,12-13-)
      "course_time": "完整的上课时间" // 例如：1-18周 星期六 1-2节
    }
    //...
    // 可以添加多个课程
  ]
}
```

解释：

- `course_id`：课程 id，例如：g20062389,**必填**
- `teacher_name`：教师名称，例如：张三,**必填**
- `week_day`：上课星期，填(1,2,3,4,5,6,7)，选填
- `class_period`：上课节次，填(1-2-,3-4-,5-6-,7-8-,9-10-11,12-13-),**别问我为什么后面要带个-，那个反人类的教务系统就是这么设计的**，选填
- `course_time`：完整的上课时间，例如：1-18 周 星期六 1-2 节，**必填，如果没有，则空着**

### 运行脚本

双击`run_app_in_venv_windows.bat`，等待运行完成，查看输出即可
