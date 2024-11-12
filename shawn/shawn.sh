#!/bin/bash
# 啟動虛擬環境
source /home/ubuntu/books/venv/bin/activate

# stone/bl 新書更新
nohup python3 /home/ubuntu/books/stone/bl/stone-update-page.py > /home/ubuntu/logs/stone-update-page.log 2>&1 &
wait  # 等待當前指令執行完畢

nohup python3 /home/ubuntu/books/stone/bl/product-upload-all-csv.py > /home/ubuntu/logs/product-upload-all-csv.log 2>&1 &
wait  # 等待當前指令執行完畢

# stone/comics 新書更新 (循環執行)
for i in {1..9}
do
    nohup python3 /home/ubuntu/books/stone/comics/${i}/stone-update-page.py > /home/ubuntu/logs/stone-comics-${i}-update.log 2>&1 &
    wait
    
    nohup python3 /home/ubuntu/books/stone/comics/${i}/product-upload.py > /home/ubuntu/logs/product-upload-comics-${i}.log 2>&1 &
    wait
done

# amazon 更新
nohup python3 /home/ubuntu/books/amazon/bl/amazon-book-bl.py > /home/ubuntu/logs/amazon-book-bl.log 2>&1 &
wait

nohup python3 /home/ubuntu/books/amazon/bl/product-upload-bl.py > /home/ubuntu/logs/product-upload-bl.log 2>&1 &
wait

nohup python3 /home/ubuntu/books/amazon/comics/amazon-book.py > /home/ubuntu/logs/amazon-book.log 2>&1 &
wait

nohup python3 /home/ubuntu/books/amazon/comics/product-upload-comics.py > /home/ubuntu/logs/product-upload-comics.log 2>&1 &
wait

# BJ4 更新
nohup python3 /home/ubuntu/books/bj4/bj4-book-update.py > /home/ubuntu/logs/bj4-book-update.log 2>&1 &
wait

nohup python3 /home/ubuntu/books/bj4/product-upload-bj4.py > /home/ubuntu/logs/product-upload-bj4.log 2>&1 &
wait

# 下架產品抓取
nohup python3 /home/ubuntu/books/refresh/not-sale-product-stone-bl.py > /home/ubuntu/logs/not-sale-product-stone-bl.log 2>&1 &
wait

nohup python3 /home/ubuntu/books/refresh/delete-same-product-csv.py > /home/ubuntu/logs/delete-same-product-csv.log 2>&1 &
wait

nohup python3 /home/ubuntu/books/refresh/delete-same-product-woocommerce.py > /home/ubuntu/logs/delete-same-product-woocommerce.log 2>&1 &
wait

# 清理重複商品
nohup python3 /home/ubuntu/books/refresh/delete-same-product-csv.py > /home/ubuntu/logs/delete-same-product-csv-refresh.log 2>&1 &
wait

nohup python3 /home/ubuntu/books/stone/bl/product-upload-all-csv.py > /home/ubuntu/logs/product-upload-all-csv-refresh.log 2>&1 &
wait

