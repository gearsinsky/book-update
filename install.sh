#!/bin/bash

# 安裝必要工具
sudo apt install -y python3.12-venv python3-pip docker.io

# 設置 Python 環境
python3 -m venv ~/books/venv
source ~/books/venv/bin/activate
pip install -r requirements.txt

# 啟動 Docker 容器
docker network create selenium-grid-network
docker run -d -p 4444:4444 --net selenium-grid-network --name selenium-hub selenium/hub:4.25.0
docker run -d --net selenium-grid-network --shm-size="2g" \
    -e SE_EVENT_BUS_HOST="selenium-hub" \
    -e SE_EVENT_BUS_PUBLISH_PORT="4442" \
    -e SE_EVENT_BUS_SUBSCRIBE_PORT="4443" \
    selenium/node-chrome:4.25.0

#設定時區
sudo timedatectl set-timezone Asia/Taipei

# 自動添加 Crontab 任務
CRON_JOBS=(
    "0 2 * * * ~/books/shawn/not-sale-comics1-9.sh >> ~/logs/not-sale-comics.log 2>&1"
    "0 5 * * * ~/books/shawn/shawn.sh >> ~/logs/shawn.log 2>&1"
)

for JOB in "${CRON_JOBS[@]}"; do
    (crontab -l 2>/dev/null | grep -F "$JOB") || (crontab -l 2>/dev/null; echo "$JOB") | crontab -
done

