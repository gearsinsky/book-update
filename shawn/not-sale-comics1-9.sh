#!/bin/bash
# 啟動虛擬環境
source /home/ubuntu/books/venv/bin/activate

# stone/comics 新書更新 (循環執行)
for i in {1..9}
do
    nohup python3 /home/ubuntu/books/refresh/${i}/not-sale-stone-${i}.py > /home/ubuntu/logs/not-sale-stone-${i}.log 2>/home/ubuntu/logs/not-sale-stone-${i}-error.log &
    wait
    
    nohup python3 /home/ubuntu/books/refresh/${i}/delete-same-product-csv-${i}.py > /home/ubuntu/logs/delete-same-product-csv-${i}.log 2>/home/ubuntu/logs/delete-same-product-csv-${i}-error.log &
    wait
done

