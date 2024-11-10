#!/bin/bash

# 获取当前时间的小时和分钟
current_hour=$(date +%H)
current_minute=$(date +%M)

# 添加crontab任务，设置在当前时刻和每天的此时刻运行
(crontab -l 2>/dev/null; echo "$current_minute $current_hour * * * cd $(pwd) && /usr/bin/python3 main.py") | crontab -

# 确保脚本有执行权限
chmod +x main.py

# 立即执行一次
python3 main.py &

echo "已设置在每天 $current_hour:$current_minute 运行main.py，并已启动首次执行"
