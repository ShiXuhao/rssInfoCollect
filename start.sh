#!/bin/bash

# 获取当前时间的小时和分钟
current_hour=$(date +%H)
current_minute=$(date +%M)

# 激活conda环境
source ~/anaconda3/etc/profile.d/conda.sh
conda activate rss

# 添加crontab任务，设置在当前时刻和每天的此时刻运行
(crontab -l 2>/dev/null; echo "$current_minute $current_hour * * * cd $(pwd) && source ~/anaconda3/etc/profile.d/conda.sh && conda activate rss && python main.py") | crontab -

# 确保脚本有执行权限
chmod +x main.py

# 使用nohup立即执行一次，并将输出重定向到nohup.out
nohup python main.py > nohup.out 2>&1 &

echo "已设置在每天 $current_hour:$current_minute 运行main.py，并已启动首次执行"
