#!/bin/bash

# 添加crontab任务
(crontab -l 2>/dev/null; echo "0 8 * * * cd $(pwd) && /usr/bin/python3 main.py") | crontab -

# 确保脚本有执行权限
chmod +x main.py

echo "已设置每天早上8点运行main.py"
